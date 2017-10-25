#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� LightBoard : admin.cgi - 2015/01/17
#�� copyright (c) KentWeb, 1997-2015
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�t�@�C���F��
require "./init.cgi";
my %cf = set_init();

# �f�[�^��
my %in = parse_form();

# �F��
check_passwd();

# ��������
if ($in{mente_log}) { mente_log(); }
if ($in{apprv_log}) { apprv_log(); }

# �Ǘ����[�h
menu_html();

#-----------------------------------------------------------
#  ���j���[���
#-----------------------------------------------------------
sub menu_html {
	header("���j���[TOP");
	print <<EOM;
<div align="center">
<p>�I���{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table class="form-tbl">
<tr>
	<th></th>
	<th width="300">�������j���[</th>
</tr><tr>
	<td class="ta-c"><input type="submit" name="mente_log" value="�I��"></td>
	<td>&nbsp; �L�������e�i���X�i�C��/�폜�j</td>
EOM

	if ($cf{approve} == 1) {
		print qq|</tr><tr>\n|;
		print qq|<td class="ta-c"><input type="submit" name="apprv_log" value="�I��"></td>\n|;
		print qq|<td>&nbsp; ���e�L���̏��F/���f</td>\n|;
	}

	print <<EOM;
</tr><tr>
	<td class="ta-c"><input type="button" value="�I��" onclick="javascript:window.location='$cf{bbs_cgi}'"></td>
	<td>&nbsp; �f���֖߂�</td>
</tr><tr>
	<td class="ta-c"><input type="button" value="�I��" onclick="javascript:window.location='$cf{admin_cgi}'"></td>
	<td>&nbsp; ���O�A�E�g</td>
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
#  �L�������e�i���X
#-----------------------------------------------------------
sub mente_log {
	# �폜����
	if ($in{job} eq "dele" && $in{no}) {

		# �폜���
		my %del;
		foreach ( split(/\0/,$in{no}) ) {
			$del{$_}++;
		}

		# �폜�����}�b�`���O
		my @data;
		open(DAT,"+< $cf{logfile}") or cgi_err("open err: $cf{logfile}");
		eval "flock(DAT, 2);";
		while (<DAT>) {
			my ($no) = (split(/<>/))[0];

			if (!defined($del{$no})) {
				push(@data,$_);
			}
		}

		# �X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# �C�����
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

		# �C���t�H�[����
		edit_form(@data);

	# �C�����s
	} elsif ($in{job} eq "edit2") {

		# �����͂̏ꍇ
		if ($in{url} eq "http://") { $in{url} = ""; }
		$in{sub} ||= "����";

		# �ǂݏo��
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

		# �X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �������b�Z�[�W
		message("�L�����C�����܂���");
	}

	# �L�������e�i���X��ʂ�\��
	header("�L�������e�i���X");
	back_btn();
	print <<EOM;
<p class="ttl">�� �L�������e�i���X</p>
<ul>
<li>������I�����đ��M�{�^���������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mente_log" value="1">
<input type="hidden" name="pass" value="$in{pass}">
�����F
<select name="job">
<option value="edit">�C��
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
EOM

	# �L����W�J
	open(IN,"$cf{logfile}") or cgi_err("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pwd,$tim) = split(/<>/);
		$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);

		print qq|<div class="art"><input type="checkbox" name="no" value="$no">\n|;
		print qq|[$no] <strong>$sub</strong> ���e�ҁF$nam �����F$dat [ <span>$hos</span> ]</div>\n|;
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
#  �C���t�H�[��
#-----------------------------------------------------------
sub edit_form {
	my ($no,$dat,$nam,$eml,$sub,$com,$url) = @_;

	$com =~ s|<br( /)?>|\n|g;
	$url ||= "http://";

	header("�L�������e�i���X &gt; �C���t�H�[��");
	back_btn('mente_log');
	print <<EOM;
<p class="ttl">���L�������e�i���X &gt; �C���t�H�[��</p>
<ul>
<li>�ύX���镔���̂ݏC�����đ��M�{�^���������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mente_log" value="1">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="no" value="$no">
<input type="hidden" name="pass" value="$in{pass}">
<table cellpadding="1" cellspacing="1">
<tr>
  <td><b>���Ȃ܂�</b></td>
  <td><input type="text" name="name" size="28" value="$nam"></td>
</tr><tr>
  <td><b>�d���[��</b></td>
  <td><input type="text" name="email" size="28" value="$eml"></td>
</tr><tr>
  <td><b>�^�C�g��</b></td>
  <td><input type="text" name="sub" size="36" value="$sub"></td>
</tr><tr>
  <td><b>�Q�Ɛ�</b></td>
  <td><input type="text" name="url" size="50" value="$url"></td>
</tr><tr>
  <td colspan="2">
    <b>���b�Z�[�W</b><br>
    <textarea name="comment" cols="60" rows="7">$com</textarea><br>
	<input type="submit" value="���M����"><input type="reset" value="���Z�b�g">
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
#  ���e�L���̏��F�E���f
#-----------------------------------------------------------
sub apprv_log {
	# ���F
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

		# �ő�L��������
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

		# �V�L��
		foreach (@data) {
			$num++;
			unshift(@log,"$num<>$_\n");
		}

		# �X�V
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �ߋ����O�X�V
		if ($cf{pastkey} && @old > 0) { make_pastlog(@old); }

		# �ꎞ�t�@�C���폜
		foreach ( split(/\0/,$in{no}) ) {
			unlink("$cf{logdir}/$_.cgi");
		}

	# �폜
	} elsif ($in{job} eq 'dele' && $in{no}) {
		foreach ( split(/\0/,$in{no}) ) {
			unlink("$cf{logdir}/$_.cgi");
		}
	}

	# �L�������e�i���X��ʂ�\��
	header("���e�L���̏��F/���f");
	back_btn();
	print <<EOM;
<p class="ttl">�� ���e�L���̏��F/���f</p>
<ul>
<li>�u���F�v���́u�폜�v��I�����đ��M�{�^���������Ă��������B��蒼���͂ł��Ȃ��̂ŐT�d�ɁI
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="apprv_log" value="1">
<input type="hidden" name="pass" value="$in{pass}">
�����F
<select name="job">
<option value="aprv">���F
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
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
		print qq|<strong>$sub</strong> ���e�ҁF<b>$nam</b> ���e���F$date [ <span>$hos</span> ]</div>\n|;
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
#  HTML�w�b�_�[
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
#  �p�X���[�h�F��
#-----------------------------------------------------------
sub check_passwd {
	# �p�X���[�h�������͂̏ꍇ�͓��̓t�H�[�����
	if ($in{pass} eq "") {
		enter_form();

	# �p�X���[�h�F��
	} elsif ($in{pass} ne $cf{password}) {
		cgi_err("�F�؂ł��܂���");
	}
}

#-----------------------------------------------------------
#  �������
#-----------------------------------------------------------
sub enter_form {
	header("�������");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>�Ǘ��p�X���[�h����</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" �F�� "><br><br>
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
#  �G���[
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
<input type="button" value="�O��ʂɖ߂�" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �������b�Z�[�W
#-----------------------------------------------------------
sub message {
	my $msg = shift;

	header("����");
	print <<EOM;
<div align="center" style="margin-top:3em;">
<hr width="350">
<p class="msg">$msg</p>
<hr width="350">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�Ǘ���ʂɖ߂�">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �߂�{�^��
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;

	print <<EOM;
<div class="ta-r">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; �O���">| : "" ]}
<input type="submit" value="�����j���[">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  �������J�b�g for Shift-JIS
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

