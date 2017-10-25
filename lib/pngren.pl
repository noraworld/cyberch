#!/usr/local/bin/perl
;#--------------------------------------------------------------------
;#
;#      SI-PNG�A���X�N���v�g Ver 1.1(2001/2/2)
;#      (c) 2000, 2001 ����
;#
;#      ���K�̎���𔺂�ʉ����E�Ĕz�z�Ȃ�
;#      ���R�ɍs���Ă��������Ă��܂��܂���B
;#
;#      �ŐV�ł̓����Ȃ�т�SI-PNG�ɂ��Ă͂�����B
;#      http://www.aurora.dti.ne.jp/~zom/Counter/index.html
;#
;#--------------------------------------------------------------------
;#
;# ���摜�A���֐��E���̏���
;#
;#      &pngren::PngRen($sipng, *narabi [, *trns [, *plte [, 0 or 1]]]);
;#      ([]���͏ȗ���)
;#
;#       $sipng     SI-PNG�t�@�C���̎w��B
;#       *narabi    �����̕��т��i�[�����z��̎Q�ƁB
;#
;#          �ȉ��͏ȗ��\�ł��B
;#
;#       *trns      ���ߏ������{���ꍇ�A"$trns{�p���b�g�ԍ�} = �����x"
;#                  �Ƃ����A�z�z��̎Q�Ƃ�n���B
;#       *plte      �p���b�g�̐F��ύX����ꍇ�A"$plte{�p���b�g�ԍ�} = �F"
;#                  �Ƃ����A�z�z��̎Q�Ƃ�n���B
;#       0 or 1     ���������ɂȂ��Ȃ�0(�������͏ȗ�)�A�c�ɂȂ��Ȃ�1�B
;#
;#--------------------------------------------------------------------
;#
;# (1) ��{�I�Ȏg����
;#
;#      require 'pngren.pl';
;#      $sipng  = './italic.png';               # SI-PNG�t�@�C���̎w��B
;#      @narabi = (1, 2, 3, 4);                 # �����̕��я����w��B
;#      &pngren::PngRen($sipng, *narabi);       # �����̘A���\���B
;#
;#
;# ���̗�����s����ƁA[1234]�ƕ\�������B
;#
;#--------------------------------------------------------------------
;#
;# (2) �C�ӂ̃p���b�g�̐F�𓧉߂��������ꍇ�̗�
;#
;#      require 'pngren.pl';
;#      $sipng   = './gothic.png';
;#      @narabi  = (0, 0, 2);   # �����܂ł͒ʏ�̗�Ɠ����B
;#      %trns    = ();
;#      $trns{0} = 0;           # 0�ԃp���b�g�̓����x��0(���S�ȓ���)�ɐݒ�B
;#      $trns{3} = 63;          # 3�ԃp���b�g�̓����x��63(75%�̓���)�ɐݒ�B
;#      &pngren::PngRen($sipng, *narabi, *trns);
;#
;#
;# ���̗�����s����ƁA0�ԃp���b�g�̐F�͊��S�ȓ��߂ɁA3�ԃp���b�g�̐F��
;# �����x63(75%�̓���)�ɏ������ꂽ��ŁA[002]�ƕ\�������B
;# �Ȃ����ƂȂ�SI-PNG�ɓ��ߏ�񂪊܂܂�Ă��Ă������ł̎w��̕���
;# �D�悳���(�܂�㏑�������)�B
;#
;# �p���b�g�ԍ��͈̔͂�0-255�B�����x�͈̔͂�0(���S�ȓ���)-255(���߂Ȃ�)�B
;#
;#--------------------------------------------------------------------
;#
;# (3) �C�ӂ̃p���b�g�̐F��ύX�������ꍇ�̗�
;#
;#      require 'pngren.pl';
;#      $sipng   = './celtic.png';
;#      @narabi  = (3, 4);      # �����܂ł͒ʏ�̗�Ɠ����B
;#      %plte    = ();
;#      $plte{0} = 'ffff00';    # 0�ԃp���b�g�̐F��'ffff00'�ɂ���B
;#                              # �F��'RRGGBB'�`���Ŏw��(html�Ɠ���)�B
;#      &pngren::PngRen($sipng, *narabi, undef, *plte);
;#                                       ^^^^^
;#                  ���E(2)�̓��ߎw����g��ʏꍇ�A������"undef"�Ƃ��Ă����B
;#
;#
;# ���̗�����s����ƁA0�ԃp���b�g�̐F�������I�ɉ��F�ɕύX���ꂽ���
;# [34]�ƕ\�������B
;#
;# �p���b�g�ԍ��͈̔͂�0-255�B�l(�F)�͈̔͂�'000000'-'ffffff'.
;#
;#--------------------------------------------------------------------
;#
;# (4) �������c�ɂȂ������ꍇ�̗�
;#
;#      &pngren::PngRen($sipng, *narabi, undef, undef, 1);
;#                                       ^^^^^  ^^^^^
;#  ���E(2)�̓��ߎw���(3)�̐F�ύX���g��ʏꍇ�A������"undef"�Ƃ��Ă����B
;#
;#--------------------------------------------------------------------
;#
;# (5) �߂�l
;#
;# &pngren::PngRen()�֐��̖߂�l�͈ȉ��̒ʂ�ł��B
;#
;#      0   ����ɏI���B
;#      1   �G���[�E�w�肳�ꂽSI-PNG�͂Ȃ��B
;#      3   �G���[�E�w�肳�ꂽ�t�@�C����SI-PNG�ł͂Ȃ��B
;#      4   �G���[�E�w�肳�ꂽSI-PNG�̓��[�}�����ŗp�̂��́B
;#      5   �G���[�E�摜���傫������(��x������16384���z����)�B
;#
;#
;# �Ȃ����̃X�N���v�g�ɂٍ͐�́uPNG�J�E���^�v�Ɠ����G���[�\��
;# ���[�`�����܂܂�Ă��܂��B����𗘗p����ɂ́A��L�́u�߂�l�v��
;# ���̂܂�"&pngren::Error()"�֐��Ɉ����Ƃ��ēn����OK�ł��B
;#
;# Ver1.0�ɂ́A�G���[�������������ł�PNG�̃w�b�_�����o�͂���Ă��܂�
;# �Ƃ����o�O������܂����B�ڂ����͖����̍X�V�������������������B
;#
;#--------------------------------------------------------------------
;#
;# �����̑��̏��
;#
;# SI-PNG�͎d�l��ő�16�܂ŉ摜�����ł��܂��B
;# �]���Ĉȉ��̂悤��SI-PNG�����݂����܂��B
;#
;#   [0123456789�j]
;#
;# �����9�̉E���Ɂu�j�v�Ƃ����摜���D�荞�܂�Ă����ł����A
;# ���́u�j�v�̉摜�����o���ɂ͂ǂ�����΂悢���A�ȉ����̕��@��
;# ���ĉ���������܂��B
;#
;#
;# (1) 11�Ԗڈȍ~�̉摜�̎��o����
;#
;# ��قǗ�Ƃ��Ă�����SI-PNG��f�Ɂu�j5000�v�Ƃ����摜��
;# �����E�A������ɂ͈ȉ��̂悤�ɃX�N���v�g�������܂��B
;#
;#      @narabi = (10, 5, 0, 0, 0);             # �����̕��я����w��B
;#      &pngren::PngRen($sipng, *narabi);       #�u�j5000�v���\�������B
;#
;# ��������Ă��C�Â���������܂��񂪁A���́u@narabi�z��v�̊e�l��
;# �������̂��̂�\���Ă���̂ł͂Ȃ��A�u�����牽�Ԗڂ̉摜���v��
;# �\���Ă���̂ł��B�]���܂��āA
;#
;# ������������������������������������������������������
;# ���O���P���Q���R���S���T���U���V���W���X��AM��PM���F��
;# ������������������������������������������������������
;#    0   1   2   3   4   5   6   7   8   9  10  11  12
;#   ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��
;#   ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��  ��
;#
;# ���̂悤�ȕ��т�SI-PNG���g���āA[PM2:55]�ƕ\������ɂ́A
;#
;#      $sipng  = 'watch.png";                 # SI-PNG���B
;#      @narabi = (11, 2, 12, 5, 5);           # �����̕��я����w��B
;#      &pngren::PngRen($sipng, *narabi);      #�uPM2:55�v���\�������B
;#
;# �Ƃ���΂悢�킯�ł��B
;#
;#
;# �Q�l�E�����Ă���摜�̐��𒲂ׂ�֐�
;#
;#      &pngren::Oshiete($sipng);
;#
;#      �߂�l�����̂܂ܓ����Ă���摜�̐���\���B
;#      �w�肳�ꂽ�t�@�C�����Ȃ�������A�����Ă����ꂪSI-PNG�ł�
;#      �Ȃ����0��Ԃ��B
;#
;#--------------------------------------------------------------------


package pngren;

# �`�����N�o�̓��[�`���B
sub ChunkDasu(){
	print pack('N', length($chunkdata) - 4).$chunkdata;
	my($crc) = 0xffffffff;
	foreach(unpack('C*', $chunkdata)){
		$crc = $crc_table[($crc ^ $_) & 0xff] ^ ($crc >> 8);
	}
	print pack('N', ~$crc);
	undef($chunkdata);
}


# CRC�p�����ݒ�B
sub CrcTable(){
	@crc_table = ();
	for(0 .. 255){
		$crc = $_;
		for(0 .. 7){
			if($crc & 1){ $crc = 0xedb88320 ^ ($crc >> 1); }
			else{ $crc = $crc >> 1; }
		}
		$crc_table[$_] = $crc;
	}
}


# ���B
sub Oshiete(){

	local($filemei) = @_;
	my($ngsa);

	unless(open(IN, $filemei)){
		return 0;
	}
	binmode(IN);
	seek(IN, 0x21,  0);
	read(IN, $ngsa, 4);
	close(IN);
	return (unpack('N', $ngsa) - 20) >> 2;
}


# ���C���B
sub PngRen(){

	local($filemei, *suuji, *trns, *plte, $muki) = @_;

	# PNG�ǂ݂Ƃ�B
	$filemei = $filemei || './pngcntr.png';
	if(!open(IN, $filemei)){ return 1; }
	binmode(IN);
	seek(IN, 0, 0);
	read(IN, $png, -s $filemei);
	close(IN);
	
	if(substr($png, 0, 0x10) ne "\x89PNG\x0d\x0a\x1a\x0a\0\0\0\x0dIHDR"){
		return 3;
	}
	if(substr($png, 0x18, 5) ne "\x08\x03\0\0\0"){ return 3; }
	if(substr($png, 0x25, 3) ne 'pgC'){ return 3; }
	if(substr($png, 0x28, 1) ne 'I'){ return 4; }
	$pgchdr = 0x29;
	
	# �A���B
	unless(@suuji){ $suuji[0] = 0; }
	$kosuu   = (unpack('N', substr($png, 0x21, 4)) - 20) >> 2;
	$pnghaba =  unpack('N', substr($png, 0x10, 4)) + 1;
	$pgcichi =  unpack('V', substr($png, $pgchdr + 16, 4));
	$x_kei   = $y_kei = 0;
	if($muki == 1){ *ren = *TateRen; }
	else{           *ren = *YokoRen; }
	
	if(&ren){ return 5; }
	# �����܂ŁB
	
	# ���������́AError()�ɏ�����n���Ă͂Ȃ��B
	
	binmode(STDOUT);
	$| = 1;
	
	&CrcTable();
	
	# PNG�w�b�_�o�́B
	print "Content-type: image/png\n\n";
	print "\x89PNG\x0d\x0a\x1a\x0a";
	
	# IHDR.
	$chunkdata = 'IHDR'.pack('N2', $x_kei, $y_kei)."\x08\x03\0\0\0";
	&ChunkDasu();
	
	# PLTE.
	($pltehjmr, $pltengsa, $trnshjmr, $trnsngsa)
		= unpack('V4', substr($png, $pgchdr, 16));
	if(%plte){ &PlteShori(); }
	else{
		print substr($png, $pltehjmr - 8, $pltengsa + 12);
		$pltengsa /= 3;
	}
	
	# tRNS.
	if(%trns){ &TrnsShori(); }
	elsif($trnsngsa){
		print substr($png, $trnshjmr - 8, $trnsngsa + 12);
	}
	
	# IDAT.
	# �����kzlib���B
	$s1 = 1;	$s2 = 0;
	foreach(unpack('C*', $ashk_src)){
		$s1 += $_;
		if($s1 > 65520){$s1 -= 65521; }
		$s2 += $s1;
		if($s2 > 65520){$s2 -= 65521; }
	}
	
	$len=pack('v', length($ashk_src));
	$chunkdata = "IDATx\x01\x01".$len.~$len.$ashk_src.pack('n2', $s2, $s1);
	&ChunkDasu();
	
	# IEND.
	print "\0\0\0\0IEND\xaeB`\x82";
	# �����܂ŁB
	
	return 0;
}


# tRNS�����B
sub TrnsShori(){

	my($trns) = "\xff" x 256;
	my($palban, $atai);

	if($trnsngsa){
		substr($trns, 0, $trnsngsa) = substr($png, $trnshjmr, $trnsngsa);
	}
	while(($palban, $atai) = each(%trns)){
		substr($trns, $palban & 255, 1) = pack('C', $atai & 255);
	}
	$trnsngsa = 256;
	while($trnsngsa--){
		if(substr($trns, $trnsngsa, 1) ne "\xff"){
			last;
		}
	}
	$trnsngsa++;
	if($trnsngsa){
		if($trnsngsa > $pltengsa){
			$trnsngsa = $pltengsa;
		}
		$chunkdata = 'tRNS'.substr($trns, 0, $trnsngsa);
		&ChunkDasu();
	}
}


# PLTE�����B
sub PlteShori(){

	my($plte) = substr($png, $pltehjmr, $pltengsa);
	my($palban, $atai);

	$pltengsa /= 3;
	while(($palban, $atai) = each(%plte)){
		$palban &= 255;
		if($palban < $pltengsa){
			$atai = hex($atai);
			$rgb  = pack('n', ($atai >> 8) & 0xffff);
			$rgb .= pack('C', $atai & 0xff);
			substr($plte, $palban * 3, 3) = $rgb;
		}
	}
	$chunkdata = 'PLTE'.$plte;
	&ChunkDasu();
}


# ���A���B
sub YokoRen(){
	
	my($ichi, @ichi, $suuji, $nmojime);
	my(@x, @y, @line) = ((), (), ());
	
	foreach $suuji (@suuji){
		if($suuji >= $kosuu){ next; }
		
		unless($x[$suuji]){
			($x[$suuji], $y[$suuji]) =
				unpack('CC', substr($png, $pgchdr + 22 + ($suuji << 2), 2));
			$ichi[$suuji] =
				unpack('v',  substr($png, $pgchdr + 20 + ($suuji << 2), 2));
		}
		unless($y_kei){
			$y_kei = $y[$suuji];
			@line  = ("\0") x $y_kei;
		}
		$x_kei += $x[$suuji];
		if(($x_kei * $y_kei) >> 15){
			return 1;
		}
		$ichi   = $pgcichi + $ichi[$suuji];
		for(0 .. $y_kei - 1){
			$line[$_] .= substr($png, $ichi, $x[$suuji]);
			$ichi     += $pnghaba;
		}
	}
	$ashk_src = join('', @line);
	return 0;
}


# �c�A���B
sub TateRen(){
	
	my($ichi, @ichi, $suuji, $y, $nmojime);
	my(@x, @y, @line) = ((), (), ());
	
	$ashk_src = '';
	foreach $suuji (@suuji){
		if($suuji >= $kosuu){ next; }
		
		unless($x[$suuji]){
			($x[$suuji], $y[$suuji]) =
				unpack('CC', substr($png, $pgchdr + 22 + ($suuji << 2), 2));
			$ichi[$suuji] = 
				unpack('v',  substr($png, $pgchdr + 20 + ($suuji << 2), 2));
		}
		unless($x_kei){ $x_kei = $x[$suuji]; }
		
		$y_kei += $y = $y[$suuji];
		if(($x_kei * $y_kei) >> 15){
			return 1;
		}
		$ichi   = $pgcichi + $ichi[$suuji];
		while($y--){
			$ashk_src .= "\0".substr($png, $ichi, $x_kei);
			$ichi     += $pnghaba;
		}
	}
	return 0;
}


# �G���[�����B
sub Error(){
	my($err) = $_[0];
	if   ($err == 0){$rgb = "\0\0\xff"; }		# ��(�w�肳�ꂽ���O���Ȃ�)
	elsif($err == 1){$rgb = "\0\xff\xff"; }		# ���F(�w�肳�ꂽPNG���Ȃ�)
	elsif($err == 2){$rgb = "\0\xff\0"; }		# ��(PNG�ł͂Ȃ�)
	elsif($err == 3){$rgb = "\xff\0\0"; }		# ��(�g����PNG)
	elsif($err == 4){$rgb = "\xff\0\xff"; }		# ��(���̃J�E���^�p�ł͂Ȃ�)
	elsif($err == 5){$rgb = "\xff\xff\0"; }		# ���F(�f�[�^�傫����)
	else            {$rgb = "\xff\xff\xff"; }	# ��(����`�ȃG���[)
	
	binmode(STDOUT);
	$| = 1;
	
	&CrcTable();
	
	print "Content-type: image/png\n\n";
	print "\x89PNG\x0d\x0a\x1a\x0a";
	print "\0\0\0\x0dIHDR\0\0\0 \0\0\0 \x01\x03\0\0\0I\xb4\xe8\xb7";
	
	$chunkdata = "PLTE\0\0\0$rgb";
	&ChunkDasu();
	
	print "\0\0\0)IDATx\xdac\xf8\x0f\x04\x0c\x0d";
	print "\x0c\x0c\x8c\xe8D\xfb\xff\xff\x0f\xd1\x89\x06\xe6\x03\x8c\x94";
	print "\x13\xf3\xff\xff\xff\x89N`s\x01\xc8i\0\xeb[9";
	print "\xa9\xb9\xc5K\xc5\0\0\0\0IEND\xaeB`\x82";
	
	exit(-1);
}
1;

# �X�V����
#
#       Ver 1.0(2000/11/1)
#           ���J�B
#
#       Ver 1.1(2001/1/28)
#           �摜�ʐς̃`�F�b�N���摜�A�����ɍs���悤�ɂ����B
#           �o�͂ł���摜�ʐς̐�����32768�o�C�g�Ɋɘa�����B
#           Ver 1.0�ł́A
#             (1) PNG�̃w�b�_���o�́B
#             (2) �G���[�`�F�b�N�B
#             (3) �摜�o�́B
#           �Ƃ������ŏ������Ă������߁A(2)�ŃG���[���o��ƃw�b�_����
#           �o�͂���Ă��܂��s����������B������ȉ��̂悤�ɏC���B
#             (1) �G���[�`�F�b�N�B
#             (2) PNG�̃w�b�_���o�́B
#             (3) �摜�o�́B
#           �܂�A�G���[�������������͉����o�͂����Ԃ��Ă���悤�ɂ����B
#
#       Ver 1.1(2001/2/2)
#           �������@���C��(VerNo�͂��̂܂�)�B
#
