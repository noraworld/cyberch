#!/usr/local/bin/perl --

#��������������������������������������������������������������������
#�� LightBoard : check.cgi - 2015/01/17
#�� copyright (c) KentWeb, 1997-2015
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C����荞��
require './init.cgi';
my %cf = set_init();

print <<EOM;
Content-type: text/html; charset=shift_jis

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# �f�[�^�t�@�C��
my %log = (
	logfile => '���O�t�@�C��',
	nofile  => '�ߋ����O�L���t�@�C��',
	numfile => '���e���F�p�ʔԃt�@�C��',
	sesfile => '�Z�b�V�����t�@�C��',
	);
foreach ( keys %log ) {
	if (-f $cf{$_}) {
		print "<li>$log{$_}�p�X : OK\n";
		if (-r $cf{$_} && -w $cf{$_}) {
			print "<li>$log{$_}�p�[�~�b�V���� : OK\n";
		} else {
			print "<li>$log{$_}�p�[�~�b�V���� : NG\n";
		}
	} else {
		print "<li>$log{$_}�p�X : NG\n";
	}
}

# �f�B���N�g��
my %dir = (
	pastdir => '�ߋ����O�f�B���N�g��',
	logdir  => '���e�p���F�f�B���N�g��',
	);
foreach ( keys(%dir) ) {
	if (-d $cf{pastdir}) {
		print "<li>$dir{$_}�f�B���N�g�� : OK\n";
		if (-r $cf{$_} && -w $cf{$_} && -x $cf{$_}) {
			print "<li>$dir{$_}�p�[�~�b�V���� : OK\n";
		} else {
			print "<li>$dir{$_}�p�[�~�b�V���� : NG\n";
		}
	} else {
		print "<li>$dir{$_}�f�B���N�g�� : NG\n";
	}
}

# �e���v���[�g
foreach (qw(bbs error find message note past enter pwd)) {
	if (-f "$cf{tmpldir}/$_.html") {
		print "<li>�e���v���[�g( $_.html ) : OK\n";
	} else {
		print "<li>�e���v���[�g( $_.html ) : NG\n";
	}
}

# Image-Magick����m�F
eval { require Image::Magick; };
if ($@) {
	print "<li>Image-Magick����: NG\n";
} else {
	print "<li>Image-Magick����: OK\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;

