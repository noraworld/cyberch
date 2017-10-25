package cap;
#������������������������������������������������������������
#�� �摜�F�؍쐬���W���[�� v3.2
#�� captcha.pl - 2012/03/13
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������
# [ �g���� ]
#
# �摜�������Í������̍쐬
# ( plain, crypt ) = cap::make( passphrase, length );
#
# �摜�F�؃`�F�b�N
# result = cap::check( plain, crypt, passphrase, time, length );
# [ result ]
#    -1 : �s��v
#     0 : ���ԃI�[�o�[
#     1 : ��v

# ���W���[���錾
use strict;
use lib "./lib";
use Crypt::RC4;

#-----------------------------------------------------------
#  ����/�Í������쐬
#-----------------------------------------------------------
sub make {
	my ($passphrase,$caplen) = @_;

	# �C�ӂ̐����𐶐�
	my @num = (0 .. 9);
	my $plain;
	srand;
	foreach (1 .. $caplen) {
		$plain .= $num[int(rand(@num))];
	}

	# ���Ԃ�t��
	$plain .= time;

	# �Í���
	my $crypt = RC4( $passphrase, $plain );
	$crypt =~ s/(.)/unpack('H2', $1)/eg;
	$crypt =~ s/\n/N/g;
	return ($plain,$crypt);
}

#-----------------------------------------------------------
#  ���e�����F��
#-----------------------------------------------------------
sub check {
	my ($input,$crypt,$passphrase,$cap_time,$caplen) = @_;

	# ���e�L�[�𕜍�
	$crypt =~ s/N/\n/g;
	$crypt =~ s/([0-9A-Fa-f]{2})/pack('H2', $1)/eg;
	my $plain = RC4( $passphrase, $crypt );

	# �L�[�Ǝ��Ԃɕ���
	$plain =~ /^(\d{$caplen})(\d+)/;
	my $code = $1;
	my $time = $2;

	# �L�[��v
	if ($input eq $code) {
		# �������ԃI�[�o�[
		if (time - $time > $cap_time * 60) {
			return 0;

		# ��������OK
		} else {
			return 1;
		}
	# �L�[�s��v
	} else {
		return -1;
	}
}


1;

