#!/usr/local/bin/perl --

#┌─────────────────────────────────
#│ LightBoard : regist.cgi - 2015/04/26
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

if ($in{mode} eq 'regist') { regist(); }
if ($in{mode} eq 'dellog') { dellog(); }
error("不明な処理です");

#-----------------------------------------------------------
#  投稿処理
#-----------------------------------------------------------
sub regist {
	# 投稿チェック
	if ($cf{postonly} && $ENV{REQUEST_METHOD} ne 'POST') {
		error("不正なリクエストです");
	}

	# 不要改行カット
	$in{sub}  =~ s|<br />||g;
	$in{name} =~ s|<br />||g;
	$in{pwd}  =~ s|<br />||g;
	$in{captcha} =~ s|<br />||g;
	$in{comment} =~ s|(<br />)+$||g;

	# チェック
	if ($cf{no_wd}) { no_wd(); }
	if ($cf{jp_wd}) { jp_wd(); }
	if ($cf{urlnum} > 0) { urlnum(); }

	$in{sub} ||= "無題";
	if ($in{url} eq "http://") { $in{url} = ''; }

	# 入力チェック
	my $err;
	if ($in{name} eq "") { $err .= "なまえの記入がありません<br />"; }
	if ($in{comment} eq "") { $err .= "コメントに記入がありません<br />"; }
	if ($in{email} ne '' && $in{email} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		$err .= "Ｅメールの入力内容が不正です<br />";
	}
	if ($in{url} ne '' && $in{url} !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/) {
		$err .= "URL情報が不正です<br />";
	}
	if ($err) { error($err); }

	# 投稿キーチェック
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		if ($in{captcha} !~ /^\d{$cf{cap_len}}$/) {
			error("投稿キーが入力不備です。<br />投稿フォームに戻って再読込み後、再入力してください");
		}

		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
		my $chk = cap::check($in{captcha},$in{str_crypt},$cf{captcha_key},$cf{cap_time},$cf{cap_len});
		if ($chk == 0) {
			error("投稿キーが制限時間を超過しました。<br />投稿フォームに戻って再読込み後、指定の数字を再入力してください");
		} elsif ($chk == -1) {
			error("投稿キーが不正です。<br />投稿フォームに戻って再読込み後、再入力してください");
		}
	}

	# ホスト取得
	my ($host,$addr) = get_host();

	# 削除キー暗号化
	my $pwd = encrypt($in{pwd}) if ($in{pwd} ne "");

	# 時間取得
	my $time = time;
	my ($min,$hour,$mday,$mon,$year,$wday) = (localtime($time))[1..6];
	my @wk = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d",
				$year+1900,$mon+1,$mday,$wk[$wday],$hour,$min);

	# 一時保存
	my $msg;
	if ($cf{approve} == 1) {
		save_tmp($date,$host,$pwd,$time);
		$msg = '記事を受理しました。記事は管理者の承認後に表示されます。';

	# 直接保存
	} else {
		save_log($date,$host,$pwd,$time);
		$msg = 'ありがとうございます。記事を受理しました。';
	}

	# クッキー格納
	set_cookie($in{name},$in{email},$in{url}) if ($in{cookie});

	# メール通知
	mail_to($date,$host) if ($cf{mailing});

	# 完了画面
	message($msg);
}

#-----------------------------------------------------------
#  ユーザ記事削除
#-----------------------------------------------------------
sub dellog {
	# 入力チェック
	$in{num} =~ s/\D//g;
	if ($in{num} eq '' or $in{pwd} eq '') {
		error("削除Noまたは削除キーが入力モレです");
	}

	my ($flg,$crypt,@log);
	open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($no,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);

		if ($in{num} == $no) {
			$flg++;
			$crypt = $pw;
			next;
		}
		push(@log,$_);
	}

	if (!$flg || $crypt eq '') {
		close(DAT);
		error("削除キーが設定されていないか又は記事が見当たりません");
	}

	# 削除キーを照合
	if (decrypt($in{pwd},$crypt) != 1) {
		close(DAT);
		error("認証できません");
	}

	# ログ更新
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 完了画面
	message("記事を削除しました");
}

#-----------------------------------------------------------
#  メール送信
#-----------------------------------------------------------
sub mail_to {
	my ($date,$host) = @_;

	# 件名をMIMEエンコード
	require './lib/jcode.pl';
	my $msub = mime_unstructured_header("BBS: $in{sub}");

	# コメント内の改行復元
	my $com = $in{comment};
	$com =~ s|<br />|\n|g;
	$com =~ s/&lt;/>/g;
	$com =~ s/&gt;/</g;
	$com =~ s/&quot;/"/g;
	$com =~ s/&amp;/&/g;
	$com =~ s/&#39;/'/g;

	# メール本文を定義
	my $mbody = <<EOM;
掲示板に投稿がありました。

投稿日：$date
ホスト：$host

件名  ：$in{sub}
お名前：$in{name}
E-mail：$in{email}
URL   ：$in{url}

$com
EOM

	my $body;
	for my $tmp ( split(/\n/,$mbody) ) {
		jcode::convert(\$tmp,'jis','sjis');
		$body .= "$tmp\n";
	}

	# メールアドレスがない場合は管理者メールに置き換え
	$in{email} ||= $cf{mailto};

	# sendmailコマンド
	my $scmd = "$cf{sendmail} -t -i";
	$scmd .= " -f $in{email}" if ($cf{sendm_f});

	# 送信
	open(MAIL,"| $scmd") or error("送信失敗");
	print MAIL "To: $cf{mailto}\n";
	print MAIL "From: $in{email}\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $cf{version}\n\n";
	print MAIL "$body\n";
	close(MAIL);
}

#-----------------------------------------------------------
#  禁止ワードチェック
#-----------------------------------------------------------
sub no_wd {
	my $flg;
	foreach ( split(/,/,$cf{no_wd}) ) {
		if (index("$in{name} $in{sub} $in{comment}", $_) >= 0) {
			$flg = 1;
			last;
		}
	}
	if ($flg) { error("禁止ワードが含まれています"); }
}

#-----------------------------------------------------------
#  日本語チェック
#-----------------------------------------------------------
sub jp_wd {
	if ($in{comment} !~ /[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]/) {
		error("メッセージに日本語が含まれていません");
	}
}

#-----------------------------------------------------------
#  URL個数チェック
#-----------------------------------------------------------
sub urlnum {
	my $com = $in{comment};
	my ($num) = ($com =~ s|(https?://)|$1|ig);
	if ($num > $cf{urlnum}) {
		error("コメント中のURLアドレスは最大$cf{urlnum}個までです");
	}
}

#-----------------------------------------------------------
#  アクセス制限
#-----------------------------------------------------------
sub get_host {
	# IP&ホスト取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}

	# IPチェック
	my $flg;
	foreach ( split(/\s+/, $cf{deny_addr}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;

		if ($addr =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		error("アクセスを許可されていません");

	# ホストチェック
	} elsif ($host) {

		foreach ( split(/\s+/, $cf{deny_host}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			error("アクセスを許可されていません");
		}
	}
	if ($host eq "") { $host = $addr; }
	return ($host,$addr);
}

#-----------------------------------------------------------
#  crypt暗号
#-----------------------------------------------------------
sub encrypt {
	my $in = shift;

	my @wd = ('a'..'z', 'A'..'Z', 0..9, '.', '/');
	srand;
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	crypt($in,$salt) || crypt ($in,'$1$'.$salt);
}

#-----------------------------------------------------------
#  crypt照合
#-----------------------------------------------------------
sub decrypt {
	my ($in, $dec) = @_;

	my $salt = $dec =~ /^\$1\$(.*)\$/ ? $1 : substr($dec,0,2);
	if (crypt($in,$salt) eq $dec || crypt($in,'$1$'.$salt) eq $dec) {
		return 1;
	} else {
		return 0;
	}
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my $msg = shift;

	open(IN,"$cf{tmpldir}/message.html") or error("open err: message.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!cmnurl!/$cf{cmnurl}/g;

	print "Content-type: text/html; charset=shift_jis\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_id}=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  記事追加
#-----------------------------------------------------------
sub save_log {
	my ($date,$host,$pwd,$time) = @_;

	open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	my $top = <DAT>;

	my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/,$top);
	if ($in{name} eq $nam && $in{comment} eq $com) {
		close(DAT);
		error("二重投稿は禁止です");
	}
	# 連続投稿チェック
	# my $flg;
	# if ($cf{regCtl} == 1) {
	# 	if ($host eq $hos && $time - $tim < $cf{wait}) { $flg = 1; }
	# } elsif ($cf{regCtl} == 2) {
	# 	if ($time - $tim < $cf{wait}) { $flg = 1; }
	# }
	# if ($flg) {
	# 	close(DAT);
	# 	error("現在投稿制限中です。もうしばらくたってから投稿をお願いします");
	# }

	# 記事No採番
	$no++;

	# 最大記事数処理
	my $i = 0;
	my (@log,@old);
	seek(DAT, 0, 0);
	while (<DAT>) {
		$i++;
		my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);

		if ($i <= $cf{maxlog} - 1) {
			push(@log,$_);
		} else {
			push(@old,$_);
		}
	}

	# 新記事
	unshift(@log,"$no<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pwd<>$time<>\n");

	# 更新
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 過去ログ更新
	if ($cf{pastkey} && @old > 0) { make_pastlog(@old);	}
}

#-----------------------------------------------------------
#  一時ファイル保存
#-----------------------------------------------------------
sub save_tmp {
	my ($date,$host,$pwd,$time) = @_;

	# 採番
	open(NO,"+< $cf{numfile}") or error("open err: $cf{numfile}");
	eval "flock(NO, 2);";
	my $num = <NO>;

	# 前ログ
	if (-e "$cf{logdir}/$num.cgi") {
		open(LOG,"$cf{logdir}/$num.cgi");
		my $log = <LOG>;
		close(LOG);

		# 連続投稿チェック
		my ($dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/,$log);
		if ($in{name} eq $nam && $in{comment} eq $com) {
			close(NO);
			error("二重投稿は禁止です");
		}
		my $flg;
		if ($cf{regCtl} == 1) {
			if ($host eq $hos && $time - $tim < $cf{wait}) { $flg = 1; }
		} elsif ($cf{regCtl} == 2) {
			if ($time - $tim < $cf{wait}) { $flg = 1; }
		}
		if ($flg) {
			close(NO);
			error("現在投稿制限中です。もうしばらくたってから投稿をお願いします");
		}
	}

	# 通番ファイル保存
	seek(NO, 0, 0);
	print NO ++$num;
	truncate(NO, tell(NO));
	close(NO);

	# ファイル生成
	open(TMP,"+> $cf{logdir}/$num.cgi") or error("write err: $num.cgi");
	eval "flock(TMP, 2);";
	print TMP "$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pwd<>$time<>";
	close(TMP);

	chmod(0666,"$cf{logdir}/$num.cgi");
}

#-----------------------------------------------------------
#  mimeエンコード
#  [quote] http://www.din.or.jp/~ohzaki/perl.htm#JP_Base64
#-----------------------------------------------------------
sub mime_unstructured_header {
  my $oldheader = shift;
  jcode::convert(\$oldheader,'euc','sjis');
  my ($header,@words,@wordstmp,$i);
  my $crlf = $oldheader =~ /\n$/;
  $oldheader =~ s/\s+$//;
  @wordstmp = split /\s+/, $oldheader;
  for ($i = 0; $i < $#wordstmp; $i++) {
    if ($wordstmp[$i] !~ /^[\x21-\x7E]+$/ and
	$wordstmp[$i + 1] !~ /^[\x21-\x7E]+$/) {
      $wordstmp[$i + 1] = "$wordstmp[$i] $wordstmp[$i + 1]";
    } else {
      push(@words, $wordstmp[$i]);
    }
  }
  push(@words, $wordstmp[-1]);
  foreach my $word (@words) {
    if ($word =~ /^[\x21-\x7E]+$/) {
      $header =~ /(?:.*\n)*(.*)/;
      if (length($1) + length($word) > 76) {
	$header .= "\n $word";
      } else {
	$header .= $word;
      }
    } else {
      $header = add_encoded_word($word, $header);
    }
    $header =~ /(?:.*\n)*(.*)/;
    if (length($1) == 76) {
      $header .= "\n ";
    } else {
      $header .= ' ';
    }
  }
  $header =~ s/\n? $//mg;
  $crlf ? "$header\n" : $header;
}
sub add_encoded_word {
  my ($str, $line) = @_;
  my $result;
  my $ascii = '[\x00-\x7F]';
  my $twoBytes = '[\x8E\xA1-\xFE][\xA1-\xFE]';
  my $threeBytes = '\x8F[\xA1-\xFE][\xA1-\xFE]';
  while (length($str)) {
    my $target = $str;
    $str = '';
    if (length($line) + 22 +
	($target =~ /^(?:$twoBytes|$threeBytes)/o) * 8 > 76) {
      $line =~ s/[ \t\n\r]*$/\n/;
      $result .= $line;
      $line = ' ';
    }
    while (1) {
      my $encoded = '=?ISO-2022-JP?B?' .
      b64encode(jcode::jis($target,'euc','z')) . '?=';
      if (length($encoded) + length($line) > 76) {
	$target =~ s/($threeBytes|$twoBytes|$ascii)$//o;
	$str = $1 . $str;
      } else {
	$line .= $encoded;
	last;
      }
    }
  }
  $result . $line;
}
# [quote] http://www.tohoho-web.com/perl/encode.htm
sub b64encode {
    my $buf = shift;
    my ($mode,$tmp,$ret);
    my $b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                . "abcdefghijklmnopqrstuvwxyz"
                . "0123456789+/";

    $mode = length($buf) % 3;
    if ($mode == 1) { $buf .= "\0\0"; }
    if ($mode == 2) { $buf .= "\0"; }
    $buf =~ s/(...)/{
        $tmp = unpack("B*", $1);
        $tmp =~ s|(......)|substr($b64, ord(pack("B*", "00$1")), 1)|eg;
        $ret .= $tmp;
    }/eg;
    if ($mode == 1) { $ret =~ s/..$/==/; }
    if ($mode == 2) { $ret =~ s/.$/=/; }

    return $ret;
}


