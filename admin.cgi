#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LightBoard : admin.cgi - 2015/01/17
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

# 認証
check_passwd();

# 条件分岐
if ($in{mente_log}) { mente_log(); }
if ($in{apprv_log}) { apprv_log(); }

# 管理モード
menu_html();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	header("メニューTOP");
	print <<EOM;
<div align="center">
<p>選択ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table class="form-tbl">
<tr>
	<th></th>
	<th width="300">処理メニュー</th>
</tr><tr>
	<td class="ta-c"><input type="submit" name="mente_log" value="選択"></td>
	<td>&nbsp; 記事メンテナンス（修正/削除）</td>
EOM

	if ($cf{approve} == 1) {
		print qq|</tr><tr>\n|;
		print qq|<td class="ta-c"><input type="submit" name="apprv_log" value="選択"></td>\n|;
		print qq|<td>&nbsp; 投稿記事の承認/反映</td>\n|;
	}

	print <<EOM;
</tr><tr>
	<td class="ta-c"><input type="button" value="選択" onclick="javascript:window.location='$cf{bbs_cgi}'"></td>
	<td>&nbsp; 掲示板へ戻る</td>
</tr><tr>
	<td class="ta-c"><input type="button" value="選択" onclick="javascript:window.location='$cf{admin_cgi}'"></td>
	<td>&nbsp; ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  記事メンテナンス
#-----------------------------------------------------------
sub mente_log {
	# 削除処理
	if ($in{job} eq "dele" && $in{no}) {

		# 削除情報
		my %del;
		foreach ( split(/\0/,$in{no}) ) {
			$del{$_}++;
		}

		# 削除情報をマッチング
		my @data;
		open(DAT,"+< $cf{logfile}") or cgi_err("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		while (<DAT>) {
			my ($no) = (split(/<>/))[0];

			if (!defined($del{$no})) {
				push(@data,$_);
			}
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# 修正画面
	} elsif ($in{job} eq "edit" && $in{no}) {

		my @data;
		open(IN,"$cf{logfile}") or cgi_err("open err: $cf{logfile}");
		while (<IN>) {
			my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pwd,$tim) = split(/<>/);

			if ($in{no} == $no) {
				@data = ($no,$dat,$nam,$eml,$sub,$com,$url);
				last;
			}
		}
		close(IN);

		# 修正フォームへ
		edit_form(@data);

	# 修正実行
	} elsif ($in{job} eq "edit2") {

		# 未入力の場合
		if ($in{url} eq "http://") { $in{url} = ""; }
		$in{sub} ||= "無題";

		# 読み出し
		my @data;
		open(DAT,"+< $cf{logfile}") or cgi_err("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		while (<DAT>) {
			my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pwd,$tim) = split(/<>/);

			if ($in{no} == $no) {
				$_ = "$no<>$dat<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$hos<>$pwd<>$tim<>\n";
			}
			push(@data,$_);
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 完了メッセージ
		message("記事を修正しました");
	}

	# 記事メンテナンス画面を表示
	header("記事メンテナンス");
	back_btn();
	print <<EOM;
<p class="ttl">■ 記事メンテナンス</p>
<ul>
<li>処理を選択して送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mente_log" value="1">
<input type="hidden" name="pass" value="$in{pass}">
処理：
<select name="job">
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
EOM

	# 記事を展開
	open(IN,"$cf{logfile}") or cgi_err("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pwd,$tim) = split(/<>/);
		$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);

		print qq|<div class="art"><input type="checkbox" name="no" value="$no">\n|;
		print qq|[$no] <strong>$sub</strong> 投稿者：$nam 日時：$dat [ <span>$hos</span> ]</div>\n|;
		print qq|<div class="com">| . cut_str($com) . qq|</div>\n|;
	}
	close(IN);

	print <<EOM;
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  修正フォーム
#-----------------------------------------------------------
sub edit_form {
	my ($no,$dat,$nam,$eml,$sub,$com,$url) = @_;

	$com =~ s|<br( /)?>|\n|g;
	$url ||= "http://";

	header("記事メンテナンス &gt; 修正フォーム");
	back_btn('mente_log');
	print <<EOM;
<p class="ttl">■記事メンテナンス &gt; 修正フォーム</p>
<ul>
<li>変更する部分のみ修正して送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mente_log" value="1">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="no" value="$no">
<input type="hidden" name="pass" value="$in{pass}">
<table cellpadding="1" cellspacing="1">
<tr>
  <td><b>おなまえ</b></td>
  <td><input type="text" name="name" size="28" value="$nam"></td>
</tr><tr>
  <td><b>Ｅメール</b></td>
  <td><input type="text" name="email" size="28" value="$eml"></td>
</tr><tr>
  <td><b>タイトル</b></td>
  <td><input type="text" name="sub" size="36" value="$sub"></td>
</tr><tr>
  <td><b>参照先</b></td>
  <td><input type="text" name="url" size="50" value="$url"></td>
</tr><tr>
  <td colspan="2">
    <b>メッセージ</b><br>
    <textarea name="comment" cols="60" rows="7">$com</textarea><br>
	<input type="submit" value="送信する"><input type="reset" value="リセット">
  </td>
</tr>
</table>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  投稿記事の承認・反映
#-----------------------------------------------------------
sub apprv_log {
	# 承認
	if ($in{job} eq 'aprv' && $in{no}) {

		my @data;
		foreach ( split(/\0/, $in{no}) ) {
			open(IN,"$cf{logdir}/$_.cgi");
			my $log = <IN>;
			close(IN);

			push(@data,$log);
		}
		my $data = @data;

		open(DAT,"+< $cf{logfile}") or cgi_err("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		my $top = <DAT>;

		my ($num) = (split(/<>/, $top))[0];

		# 最大記事数処理
		my $i = 0;
		my (@log,@old);
		seek(DAT, 0, 0);
		while (<DAT>) {
			$i++;
			my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);

			if ($i <= $cf{maxlog} - $data) {
				push(@log,$_);
			} else {
				push(@old,$_);
			}
		}

		# 新記事
		foreach (@data) {
			$num++;
			unshift(@log,"$num<>$_\n");
		}

		# 更新
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 過去ログ更新
		if ($cf{pastkey} && @old > 0) { make_pastlog(@old); }

		# 一時ファイル削除
		foreach ( split(/\0/,$in{no}) ) {
			unlink("$cf{logdir}/$_.cgi");
		}

	# 削除
	} elsif ($in{job} eq 'dele' && $in{no}) {
		foreach ( split(/\0/,$in{no}) ) {
			unlink("$cf{logdir}/$_.cgi");
		}
	}

	# 記事メンテナンス画面を表示
	header("投稿記事の承認/反映");
	back_btn();
	print <<EOM;
<p class="ttl">■ 投稿記事の承認/反映</p>
<ul>
<li>「承認」又は「削除」を選択して送信ボタンを押してください。やり直しはできないので慎重に！
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="apprv_log" value="1">
<input type="hidden" name="pass" value="$in{pass}">
処理：
<select name="job">
<option value="aprv">承認
<option value="dele">削除
</select>
<input type="submit" value="送信する">
EOM

	opendir(DIR,"$cf{logdir}");
	while( $_ = readdir(DIR) ) {
		next if (!/^(\d+)\.cgi$/);

		my $num = $1;
		open(IN,"$cf{logdir}/$num.cgi");
		my $log = <IN>;
		close(IN);

		my ($date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/,$log);
		print qq|<div class="art"><input type="checkbox" name="no" value="$num">\n|;
		print qq|<strong>$sub</strong> 投稿者：<b>$nam</b> 投稿日：$date [ <span>$hos</span> ]</div>\n|;
		print qq|<div class="com">$com</div>\n|;
	}
	closedir(DIR);

	print <<EOM;
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print <<EOM;
Content-type: text/html; charset=shift_jis

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; font-family:Verdana,"MS PGothic",Osaka,Arial,sans-serif; }
p.ttl { font-weight:bold; color:#004080; border-bottom:1px solid #004080; padding:3px; }
p.err { color:#dd0000; }
p.msg { color:#006400; }
table.form-tbl { border:1px solid #8080C0; border-collapse:collapse; margin:1em auto; }
table.form-tbl th { border:1px solid #8080C0; background:#DCDCED; padding:6px; }
table.form-tbl td { border:1px solid #8080C0; background:#fff; padding:6px; }
.ta-r { text-align:right; }
.ta-c { text-align:center; }
div.art { border-top:1px dotted gray; padding:5px; margin-top:10px; }
div.art span, div.art strong { color:green; }
div.com { margin-left:2em; color:#804000; font-size:90%; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		enter_form();

	# パスワード認証
	} elsif ($in{pass} ne $cf{password}) {
		cgi_err("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	header("入室画面");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>管理パスワード入力</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" 認証 "><br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  エラー
#-----------------------------------------------------------
sub cgi_err {
	my $err = shift;

	header("ERROR!");
	print <<EOM;
<div align="center">
<hr width="350">
<h3>ERROR!</h3>
<p class="err">$err</p>
<hr width="350">
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my $msg = shift;

	header("完了");
	print <<EOM;
<div align="center" style="margin-top:3em;">
<hr width="350">
<p class="msg">$msg</p>
<hr width="350">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="管理画面に戻る">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  戻りボタン
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;

	print <<EOM;
<div class="ta-r">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; 前画面">| : "" ]}
<input type="submit" value="▲メニュー">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  文字数カット for Shift-JIS
#-----------------------------------------------------------
sub cut_str {
	my $str = shift;
	$str =~ s|<br( /)?>||g;

	my $i = 0;
	my $ret;
	while($str =~ /([\x00-\x7F\xA1-\xDF]|[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC])/gx) {
		$i++;
		$ret .= $1;
		last if ($i >= 40);
	}
	return $ret;
}

