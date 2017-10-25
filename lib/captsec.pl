#��������������������������������������������������������������������
#�� �摜�F�؍쐬�t�@�C�� [ GD::SecurityImage + Image::Magick ]
#�� captsec.pl - 2011/07/03
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

#-----------------------------------------------------------
#  �F�؉摜�쐬 [���W���[����]
#-----------------------------------------------------------
sub load_capsec {
	my ($plain, $font) = @_;

	# �摜����
	# [����] �X�N�����u�����[�h(0=no 1=yes) : �摜�ʒu���U��΂�@�\
	#        �摜���T�C�Y, �摜�c�T�C�Y, �摜�������؂���̐�,
	#        �t�H���g�t�@�C��, �t�H���g�T�C�Y
	use GD::SecurityImage use_magick => 1;
	my $image = GD::SecurityImage->new(
					scramble => 0,
					width    => 90,
					height   => 26,
					lines    => 8,
					font     => $font,
					ptsize   => 18,
	);
	$image->random($plain);
	$image->create("ttf", "ellipse");
	$image->particle(100); # �w�i�ɎU��΂߂�h�b�g��

	# �摜�o��
	my ($img_out) = $image->out(force => "png");

	# �摜�\��
	print "Content-type: image/png\n\n";
	binmode(STDOUT);
	print STDOUT $img_out;
	exit;
}


1;

