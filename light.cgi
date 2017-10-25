#!/usr/local/bin/perl --

#┌─────────────────────────────────
#│ LightBoard : light.cgi - 2015/04/25
#│ copyright (c) KentWeb, 1997-2015
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定ファイル認識
require "./init.cgi";
my %cf = set_init();

# データ受理
my %in = parse_form();

# アクセス制限
passwd(%in) if ($cf{enter_pwd} ne '');

# 処理分岐
if ($in{mode} eq 'find') { find_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'past') { past_page(); }
bbs_list();

#-----------------------------------------------------------
#  記事表示
#-----------------------------------------------------------
sub bbs_list {
	# 記事の修正・削除
	if ($in{edit} or $in{dele}) { edit_conf(); }
	
	# レス処理
	$in{res} =~ s/\D//g;
	my %res;
	if ($in{res}) {
		my $flg;
		open(IN,"$cf{logfile}") or error("open err: $cf{logfile}");
		while (<IN>) {
			my ($no,$sub,$com) = (split(/<>/))[0,4,5];
			if ($in{res} == $no) {
				$flg++;
				$res{sub} = $sub;
				$res{com} = $com;
				last;
			}
		}
		close(IN);
		
		if (!$flg) { error("該当記事が見つかりません"); }
		
		$res{sub} =~ s/^Re://g;
		$res{sub} =~ s/\[\d+\]\s?//g;
		$res{sub} = "Re:[$in{res}] $res{sub}";
		$res{com} = "&gt; $res{com}";
		$res{com} =~ s|<br( /)?>|\n&gt; |ig;
	}
	
	# ページ数定義
	my $pg = $in{pg} || 0;
	
	# データオープン
	my ($i,@log);
	open(IN,"$cf{logfile}") or error("open err: $cf{logfile}");
	while (<IN>) {
		$i++;
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{pg_max});
		
		push(@log,$_);
	}
	close(IN);
	
	# 繰越ボタン作成
	my $page_btn = make_pager($i,$pg);
	
	# クッキー取得
	my @cook = get_cookie();
	$cook[2] ||= 'http://';
	
	# home or logoff
	my $home = $cf{enter_pwd} eq '' ? $cf{homepage} : "$cf{bbs_cgi}?mode=logoff";
	
	# テンプレート読込
	open(IN,"$cf{tmpldir}/bbs.html") or error("open err: bbs.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	# 文字置き換え
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!homepage!/$home/g;
	$tmpl =~ s/<!-- page_btn -->/$page_btn/g;
	$tmpl =~ s/!name!/$cook[0]/;
	$tmpl =~ s/!email!/$cook[1]/;
	$tmpl =~ s/!url!/$cook[2]/;
	$tmpl =~ s/!sub!/$res{sub}/;
	$tmpl =~ s/!comment!/$res{com}/;
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s/!pg!/$pg/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="" class="icon" />|g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make($cf{captcha_key},$cf{cap_len});
		$tmpl =~ s/!str_crypt!/$str_crypt/g;
	} else {
		$tmpl =~ s/<!-- captcha_begin -->.+<!-- captcha_end -->//s;
	}
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s
			? ($1,$2,$3)
			: error("テンプレート不正");

	# ヘッダ表示
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $head;
	
	# ループ部
	foreach (@log) {
		my ($no,$date,$name,$eml,$sub,$com,$url,$host,$pw,$tim) = split(/<>/);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$com = auto_link($com) if ($cf{auto_link});
		$com =~ s/([>]|^)(&gt;[^<]*)/$1<span style="color:$cf{ref_col}">$2<\/span>/g if ($cf{ref_col});
		$com .= qq|<p class="url"><a href="$url" target="_blank">$url</a></p>| if ($url);
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!name!/$name/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!comment!/$com/g;
		$tmp =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  ワード検索
#-----------------------------------------------------------
sub find_data {
	# 条件
	$in{cond} =~ s/\D//g;
	$in{word} =~ s|<br />||g;
	
	# 検索条件プルダウン
	my %op = (1 => 'AND', 0 => 'OR');
	my $op_cond;
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op_cond .= qq|<option value="$_" selected="selected">$op{$_}</option>\n|;
		} else {
			$op_cond .= qq|<option value="$_">$op{$_}</option>\n|;
		}
	}
	
	# 検索実行
	my ($hit,@log) = search($in{word},$in{cond},$cf{logfile}) if ($in{word} ne '');
	
	# テンプレート
	open(IN,"$cf{tmpldir}/find.html") or error("open err: find.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s/<!-- op_cond -->/$op_cond/;
	$tmpl =~ s/!word!/$in{word}/;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	# 分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s
			? ($1,$2,$3)
			: error('テンプレート不正');

	# ヘッダ部
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $head;
	
	# ループ部
	foreach (@log) {
		my ($no,$date,$name,$eml,$sub,$com,$url,$host,$pw,$tim) = split(/<>/);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$com  = auto_link($com) if ($cf{auto_link});
		$com =~ s/([>]|^)(&gt;[^<]*)/$1<span style="color:$cf{ref_col}">$2<\/span>/g if ($cf{ref_col});
		$url  = qq|&lt;<a href="$url" target="_blank">URL</a>&gt;| if ($url);
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$name/g;
		$tmp =~ s/!home!/$url/g;
		$tmp =~ s/!comment!/$com/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  検索実行
#-----------------------------------------------------------
sub search {
	my ($word,$cond,$file,$list) = @_;
	
	# キーワードを配列化
	$word =~ s/\x81\x40/ /g;
	my @wd = split(/\s+/,$word);
	
	# キーワード検索準備（Shift-JIS定義）
	my $ascii = '[\x00-\x7F]';
	my $hanka = '[\xA1-\xDF]';
	my $kanji = '[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]';
	
	# 検索処理
	my ($i,@log);
	open(IN,"$file") or error("open err: $file");
	while (<IN>) {
		my ($no,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);
		
		my $flg;
		foreach my $wd (@wd) {
			if ("$nam $eml $sub $com $url" =~ /^(?:$ascii|$hanka|$kanji)*?\Q$wd\E/i) {
				$flg++;
				if ($cond == 0) { last; }
			} else {
				if ($cond == 1) { $flg = 0; last; }
			}
		}
		next if (!$flg);
		
		$i++;
		if ($list > 0) {
			next if ($i < $in{pg} + 1);
			next if ($i > $in{pg} + $list);
		}
		
		push(@log,$_);
	}
	close(IN);
	
	# 検索結果
	return ($i,@log);
}

#-----------------------------------------------------------
#  過去ログページ
#-----------------------------------------------------------
sub past_page {
	# 過去ログ番号
	open(IN,"$cf{nofile}") or error("open err: $cf{nofile}");
	my $pastnum = <IN>;
	close(IN);
	
	my $pastnum = sprintf("%04d",$pastnum);
	$in{pno} =~ s/\D//g;
	$in{pno} ||= $pastnum;
	
	# プルダウンタグ作成
	my $op_pno;
	for ( my $i = $pastnum; $i > 0; $i-- ) {
		$i = sprintf("%04d",$i);
		
		if ($in{pno} == $i) {
			$op_pno .= qq|<option value="$i" selected="selected">$i</option>\n|;
		} else {
			$op_pno .= qq|<option value="$i">$i</option>\n|;
		}
	}
	
	# ページ数
	my $pg = $in{pg} || 0;
	
	# 初期化
	my ($hit,$page_btn,@log);
	
	# 対象ログ定義
	my $file = "$cf{pastdir}/" . sprintf("%04d", $in{pno}) . ".cgi";
	
	# ワード検索
	if ($in{find} && $in{word} ne '') {
		# 検索
		($hit,@log) = search($in{word},$in{cond},$file,$in{list});
		
		# 結果
		$page_btn = "検索結果：<b>$hit</b>件 &nbsp;&nbsp;" . pgbtn_old($hit,$in{pno},$pg,'past');
	
	# ログ一覧
	} else {
		# 過去ログオープン
		my $i = 0;
		open(IN,"$file") or error("open err: $file");
		while(<IN>) {
			$i++;
			next if ($i < $pg + 1);
			next if ($i > $pg + $cf{pg_max});
			
			push(@log,$_);
		}
		close(IN);
		
		# 繰越ボタン作成
		$page_btn = pgbtn_old($i,$in{pno},$pg);
	}
	
	# プルダウン作成（検索条件）
	my %op = make_op();
	
	# テンプレート読み込み
	my ($flg,$loop);
	open(IN,"$cf{tmpldir}/past.html") or error("open err: past.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!past_num!/$in{pno}/g;
	$tmpl =~ s/!bbs_url!/$cf{html_url}\/index.html/g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/<!-- op_pno -->/$op_pno/g;
	$tmpl =~ s/<!-- op_(\w+) -->/$op{$1}/g;
	$tmpl =~ s/!word!/$in{word}/g;
	$tmpl =~ s/!page_btn!/$page_btn/g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s
			? ($1,$2,$3)
			: error('テンプレート不正');
	
	if ($in{change}) { $in{word} = ''; }
	
	# 画面表示
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $head;
	foreach (@log) {
		my ($no,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);
		$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);
		$com = auto_link($com) if ($cf{auto_link});
		$com =~ s/([>]|^)(&gt;[^<]*)/$1<span style="color:$cf{ref_col}">$2<\/span>/g if ($cf{ref_col});
		$url = qq|&lt;<a href="$url" target="_blank">URL</a>&gt;| if ($url);
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$nam/g;
		$tmp =~ s/!home!/$url/g;
		$tmp =~ s/!comment!/$com/g;
		print $tmp;
	}
	
	# フッタ
	print footer($foot);
	exit;
}

#-----------------------------------------------------------
#  留意事項表示
#-----------------------------------------------------------
sub note_page {
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  自動リンク
#-----------------------------------------------------------
sub auto_link {
	my $text = shift;
	
	$text =~ s/(s?https?:\/\/([\w-.!~*'();\/?:\@=+\$,%#]|&amp;)+)/<a href="$1" target="_blank">$1<\/a>/g;
	return $text;
}

#-----------------------------------------------------------
#  ページ送り作成
#-----------------------------------------------------------
sub make_pager {
	my ($i,$pg) = @_;
	
	# ページ繰越数定義
	$cf{pg_max} ||= 10;
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};
	
	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<li><span>$x</span></li>\n!);
			} else {
				push(@pg,qq!<li><a href="$cf{bbs_cgi}?pg=$y">$x</a></li>\n!);
			}
			$x++;
			$y += $cf{pg_max};
			$z -= $cf{pg_max};
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('', @pg);
	if ($back >= 0) {
		$ret = qq!<li><a href="$cf{bbs_cgi}?pg=$back">&laquo;</a></li>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<li><a href="$cf{bbs_cgi}?pg=$next">&raquo;</a></li>\n!;
	}
	
	# 結果を返す
	return $ret ? qq|<ul class="pager">\n$ret</ul>| : '';
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};

	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/, $cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URLデコード
	my @cook;
	foreach ( split(/<>/, $cook{$cf{cookie_id}}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  繰越ボタン作成 [ 過去ログ ]
#-----------------------------------------------------------
sub pgbtn_old {
	my ($i,$pno,$pg,$stat) = @_;

	# ページ繰越定義
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};

	my $link;
	if ($stat eq 'past') {
		my $wd = url_enc($in{word});
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno&amp;find=1&amp;word=$wd";
	} else {
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno";
	}

	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<li><span>$x</span></li>\n!);
			} else {
				push(@pg,qq!<li><a href="$link&amp;pg=$y">$x</a></li>\n!);
			}
			$x++;
			$y += $cf{pg_max};
			$i -= $cf{pg_max};
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('', @pg);
	if ($back >= 0) {
		$ret = qq!<li><a href="$link&amp;pg=$back">&laquo;</a></li>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<li><a href="$link&amp;pg=$next">&raquo;</a></li>\n!;
	}
	
	# 結果を返す
	return $ret ? qq|<ul class="pager">\n$ret</ul>| : '';
}

#-----------------------------------------------------------
#  プルダウン作成 [ 検索条件 ]
#-----------------------------------------------------------
sub make_op {
	my %op;
	my %cond = (1 => 'AND', 0 => 'OR');
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op{cond} .= qq|<option value="$_" selected="selected">$cond{$_}</option>\n|;
		} else {
			$op{cond} .= qq|<option value="$_">$cond{$_}</option>\n|;
		}
	}
	for ( my $i = 10; $i <= 30; $i += 5 ) {
		if ($in{list} == $i) {
			$op{list} .= qq|<option value="$i" selected="selected">$i件</option>\n|;
		} else {
			$op{list} .= qq|<option value="$i">$i件</option>\n|;
		}
	}
	return %op;
}

#-----------------------------------------------------------
#  URLエンコード
#-----------------------------------------------------------
sub url_enc {
	local($_) = @_;

	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-----------------------------------------------------------
#  記事削除確認
#-----------------------------------------------------------
sub edit_conf {
	my %log;
	open(IN,"$cf{logfile}") or error("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$name,$eml,$sub,$com,$url,$host,$pw,$tim) = split(/<>/);
		if ($in{edit} == $no or $in{dele} == $no) {
			$log{flg}++;
			$log{num}  = $no;
			$log{sub}  = $sub;
			$log{date} = $date;
			$log{name} = $name;
			last;
		}
	}
	close(IN);
	
	if (!$log{flg}) { error("該当記事が見つかりません"); }
	
	open(IN,"$cf{tmpldir}/pwd.html") or error("open err: pwd.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	my $pg = $in{pg} || 0;
	$tmpl =~ s/!(\w+_\w+)!/$cf{$1}/g;
	$tmpl =~ s/!(sub|name|date|num)!/$log{$1}/g;
	$tmpl =~ s/!pg!/$pg/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="" class="icon" />|g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;
	
	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

