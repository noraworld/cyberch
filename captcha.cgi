#!/usr/local/bin/perl

#������������������������������������������������������������
#�� �摜�F�؍쐬�t�@�C�� v3.2
#�� captcha.cgi - 2015/01/17
#�� copyright (c) KentWeb, 1997-2015
#�� http://www.kent-web.com/
#������������������������������������������������������������

# ���W���[���錾
use strict;
use lib "./lib";
use Crypt::RC4;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = set_init();

# �p�����[�^�󂯎��
my $buf = $ENV{QUERY_STRING};
$buf =~ s/[<>&"'\s]//g;
err_img() if (!$buf);

# ����
my $plain = decrypt($cf{cap_len});

# �F�؉摜�쐬
if ($cf{use_captcha} == 2) {
	require $cf{captsec_pl};
	load_capsec($plain,"$cf{bin_dir}/$cf{font_ttl}");
} else {
	load_pngren($plain,"$cf{bin_dir}/$cf{si_png}");
}

#-----------------------------------------------------------
#  �F�؉摜�쐬 [���C�u������]
#-----------------------------------------------------------
sub load_pngren {
	my ($plain,$sipng) = @_;

	# ����
	my @img = split(//,$plain);

	# �\���J�n
	require $cf{pngren_pl};
	pngren::PngRen($sipng,\@img);
	exit;
}

#-----------------------------------------------------------
#  ����
#-----------------------------------------------------------
sub decrypt {
	my $caplen = shift;

	# ����
	$buf =~ s/N/\n/g;
	$buf =~ s/([0-9A-Fa-f]{2})/pack('H2',$1)/eg;
	my $plain = RC4($cf{captcha_key},$buf);

	# �擪�̐����𒊏o
	$plain =~ s/^(\d{$caplen}).*/$1/ or err_img();
	return $plain;
}

#-----------------------------------------------------------
#  �G���[����
#-----------------------------------------------------------
sub err_img {
	# �G���[�摜
	my @err = qw{
		47 49 46 38 39 61 2d 00 0f 00 80 00 00 00 00 00 ff ff ff 2c
		00 00 00 00 2d 00 0f 00 00 02 49 8c 8f a9 cb ed 0f a3 9c 34
		81 7b 03 ce 7a 23 7c 6c 00 c4 19 5c 76 8e dd ca 96 8c 9b b6
		63 89 aa ee 22 ca 3a 3d db 6a 03 f3 74 40 ac 55 ee 11 dc f9
		42 bd 22 f0 a7 34 2d 63 4e 9c 87 c7 93 fe b2 95 ae f7 0b 0e
		8b c7 de 02	00 3b
	};

	print "Content-type: image/gif\n\n";
	foreach (@err) {
		print pack('C*', hex($_));
	}
	exit;
}

