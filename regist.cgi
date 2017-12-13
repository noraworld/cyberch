#!/usr/local/bin/perl --

#��������������������������������������������������������������������
#�� LightBoard : regist.cgi - 2015/04/26
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

# �A�N�Z�X����
passwd(%in) if ($cf{enter_pwd} ne '');

if ($in{mode} eq 'regist') { regist(); }
if ($in{mode} eq 'dellog') { dellog(); }
error("�s���ȏ����ł�");

#-----------------------------------------------------------
#  ���e����
#-----------------------------------------------------------
sub regist {
	# ���e�`�F�b�N
	if ($cf{postonly} && $ENV{REQUEST_METHOD} ne 'POST') {
		error("�s���ȃ��N�G�X�g�ł�");
	}

	# �s�v���s�J�b�g
	$in{sub}  =~ s|<br />||g;
	$in{name} =~ s|<br />||g;
	$in{pwd}  =~ s|<br />||g;
	$in{captcha} =~ s|<br />||g;
	$in{comment} =~ s|(<br />)+$||g;

	# �`�F�b�N
	if ($cf{no_wd}) { no_wd(); }
	if ($cf{jp_wd}) { jp_wd(); }
	if ($cf{urlnum} > 0) { urlnum(); }

	$in{sub} ||= "����";
	if ($in{url} eq "http://") { $in{url} = ''; }

	# ���̓`�F�b�N
	my $err;
	if ($in{name} eq "") { $err .= "�Ȃ܂��̋L��������܂���<br />"; }
	if ($in{comment} eq "") { $err .= "�R�����g�ɋL��������܂���<br />"; }
	if ($in{email} ne '' && $in{email} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		$err .= "�d���[���̓��͓��e���s���ł�<br />";
	}
	if ($in{url} ne '' && $in{url} !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/) {
		$err .= "URL��񂪕s���ł�<br />";
	}
	if ($err) { error($err); }

	# ���e�L�[�`�F�b�N
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		if ($in{captcha} !~ /^\d{$cf{cap_len}}$/) {
			error("���e�L�[�����͕s���ł��B<br />���e�t�H�[���ɖ߂��čēǍ��݌�A�ē��͂��Ă�������");
		}

		# ���e�L�[�`�F�b�N
		# -1 : �L�[�s��v
		#  0 : �������ԃI�[�o�[
		#  1 : �L�[��v
		my $chk = cap::check($in{captcha},$in{str_crypt},$cf{captcha_key},$cf{cap_time},$cf{cap_len});
		if ($chk == 0) {
			error("���e�L�[���������Ԃ𒴉߂��܂����B<br />���e�t�H�[���ɖ߂��čēǍ��݌�A�w��̐������ē��͂��Ă�������");
		} elsif ($chk == -1) {
			error("���e�L�[���s���ł��B<br />���e�t�H�[���ɖ߂��čēǍ��݌�A�ē��͂��Ă�������");
		}
	}

	# �z�X�g�擾
	my ($host,$addr) = get_host();

	# �폜�L�[�Í���
	my $pwd = encrypt($in{pwd}) if ($in{pwd} ne "");

	# ���Ԏ擾
	my $time = time;
	my ($min,$hour,$mday,$mon,$year,$wday) = (localtime($time))[1..6];
	my @wk = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d",
				$year+1900,$mon+1,$mday,$wk[$wday],$hour,$min);

	# �ꎞ�ۑ�
	my $msg;
	if ($cf{approve} == 1) {
		save_tmp($date,$host,$pwd,$time);
		$msg = '�L�����󗝂��܂����B�L���͊Ǘ��҂̏��F��ɕ\������܂��B';

	# ���ڕۑ�
	} else {
		save_log($date,$host,$pwd,$time);
		$msg = '���肪�Ƃ��������܂��B�L�����󗝂��܂����B';
	}

	# �N�b�L�[�i�[
	set_cookie($in{name},$in{email},$in{url}) if ($in{cookie});

	# ���[���ʒm
	mail_to($date,$host) if ($cf{mailing});

	# �������
	message($msg);
}

#-----------------------------------------------------------
#  ���[�U�L���폜
#-----------------------------------------------------------
sub dellog {
	# ���̓`�F�b�N
	$in{num} =~ s/\D//g;
	if ($in{num} eq '' or $in{pwd} eq '') {
		error("�폜No�܂��͍폜�L�[�����̓����ł�");
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
		error("�폜�L�[���ݒ肳��Ă��Ȃ������͋L������������܂���");
	}

	# �폜�L�[���ƍ�
	if (decrypt($in{pwd},$crypt) != 1) {
		close(DAT);
		error("�F�؂ł��܂���");
	}

	# ���O�X�V
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# �������
	message("�L�����폜���܂���");
}

#-----------------------------------------------------------
#  ���[�����M
#-----------------------------------------------------------
sub mail_to {
	my ($date,$host) = @_;

	# ������MIME�G���R�[�h
	require './lib/jcode.pl';
	my $msub = mime_unstructured_header("BBS: $in{sub}");

	# �R�����g���̉��s����
	my $com = $in{comment};
	$com =~ s|<br />|\n|g;
	$com =~ s/&lt;/>/g;
	$com =~ s/&gt;/</g;
	$com =~ s/&quot;/"/g;
	$com =~ s/&amp;/&/g;
	$com =~ s/&#39;/'/g;

	# ���[���{�����`
	my $mbody = <<EOM;
�f���ɓ��e������܂����B

���e���F$date
�z�X�g�F$host

����  �F$in{sub}
�����O�F$in{name}
E-mail�F$in{email}
URL   �F$in{url}

$com
EOM

	my $body;
	for my $tmp ( split(/\n/,$mbody) ) {
		jcode::convert(\$tmp,'jis','sjis');
		$body .= "$tmp\n";
	}

	# ���[���A�h���X���Ȃ��ꍇ�͊Ǘ��҃��[���ɒu������
	$in{email} ||= $cf{mailto};

	# sendmail�R�}���h
	my $scmd = "$cf{sendmail} -t -i";
	$scmd .= " -f $in{email}" if ($cf{sendm_f});

	# ���M
	open(MAIL,"| $scmd") or error("���M���s");
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
#  �֎~���[�h�`�F�b�N
#-----------------------------------------------------------
sub no_wd {
	my $flg;
	foreach ( split(/,/,$cf{no_wd}) ) {
		if (index("$in{name} $in{sub} $in{comment}", $_) >= 0) {
			$flg = 1;
			last;
		}
	}
	if ($flg) { error("�֎~���[�h���܂܂�Ă��܂�"); }
}

#-----------------------------------------------------------
#  ���{��`�F�b�N
#-----------------------------------------------------------
sub jp_wd {
	if ($in{comment} !~ /[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]/) {
		error("���b�Z�[�W�ɓ��{�ꂪ�܂܂�Ă��܂���");
	}
}

#-----------------------------------------------------------
#  URL���`�F�b�N
#-----------------------------------------------------------
sub urlnum {
	my $com = $in{comment};
	my ($num) = ($com =~ s|(https?://)|$1|ig);
	if ($num > $cf{urlnum}) {
		error("�R�����g����URL�A�h���X�͍ő�$cf{urlnum}�܂łł�");
	}
}

#-----------------------------------------------------------
#  �A�N�Z�X����
#-----------------------------------------------------------
sub get_host {
	# IP&�z�X�g�擾
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}

	# IP�`�F�b�N
	my $flg;
	foreach ( split(/\s+/, $cf{deny_addr}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;

		if ($addr =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		error("�A�N�Z�X��������Ă��܂���");

	# �z�X�g�`�F�b�N
	} elsif ($host) {

		foreach ( split(/\s+/, $cf{deny_host}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			error("�A�N�Z�X��������Ă��܂���");
		}
	}
	if ($host eq "") { $host = $addr; }
	return ($host,$addr);
}

#-----------------------------------------------------------
#  crypt�Í�
#-----------------------------------------------------------
sub encrypt {
	my $in = shift;

	my @wd = ('a'..'z', 'A'..'Z', 0..9, '.', '/');
	srand;
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	crypt($in,$salt) || crypt ($in,'$1$'.$salt);
}

#-----------------------------------------------------------
#  crypt�ƍ�
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
#  �������b�Z�[�W
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
#  �N�b�L�[���s
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# �����t�H�[�}�b�g
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URL�G���R�[�h
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_id}=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  �L���ǉ�
#-----------------------------------------------------------
sub save_log {
	my ($date,$host,$pwd,$time) = @_;

	open(DAT,"+< $cf{logfile}") or error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	my $top = <DAT>;

	my ($no,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/,$top);
	if ($in{name} eq $nam && $in{comment} eq $com) {
		close(DAT);
		error("��d���e�͋֎~�ł�");
	}
	# �A�����e�`�F�b�N
	# my $flg;
	# if ($cf{regCtl} == 1) {
	# 	if ($host eq $hos && $time - $tim < $cf{wait}) { $flg = 1; }
	# } elsif ($cf{regCtl} == 2) {
	# 	if ($time - $tim < $cf{wait}) { $flg = 1; }
	# }
	# if ($flg) {
	# 	close(DAT);
	# 	error("���ݓ��e�������ł��B�������΂炭�����Ă��瓊�e�����肢���܂�");
	# }

	# �L��No�̔�
	$no++;

	# �ő�L��������
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

	# �V�L��
	unshift(@log,"$no<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pwd<>$time<>\n");

	# �X�V
	seek(DAT, 0, 0);
	print DAT @log;
	truncate(DAT, tell(DAT));
	close(DAT);

	# �ߋ����O�X�V
	if ($cf{pastkey} && @old > 0) { make_pastlog(@old);	}
}

#-----------------------------------------------------------
#  �ꎞ�t�@�C���ۑ�
#-----------------------------------------------------------
sub save_tmp {
	my ($date,$host,$pwd,$time) = @_;

	# �̔�
	open(NO,"+< $cf{numfile}") or error("open err: $cf{numfile}");
	eval "flock(NO, 2);";
	my $num = <NO>;

	# �O���O
	if (-e "$cf{logdir}/$num.cgi") {
		open(LOG,"$cf{logdir}/$num.cgi");
		my $log = <LOG>;
		close(LOG);

		# �A�����e�`�F�b�N
		my ($dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/,$log);
		if ($in{name} eq $nam && $in{comment} eq $com) {
			close(NO);
			error("��d���e�͋֎~�ł�");
		}
		my $flg;
		if ($cf{regCtl} == 1) {
			if ($host eq $hos && $time - $tim < $cf{wait}) { $flg = 1; }
		} elsif ($cf{regCtl} == 2) {
			if ($time - $tim < $cf{wait}) { $flg = 1; }
		}
		if ($flg) {
			close(NO);
			error("���ݓ��e�������ł��B�������΂炭�����Ă��瓊�e�����肢���܂�");
		}
	}

	# �ʔԃt�@�C���ۑ�
	seek(NO, 0, 0);
	print NO ++$num;
	truncate(NO, tell(NO));
	close(NO);

	# �t�@�C������
	open(TMP,"+> $cf{logdir}/$num.cgi") or error("write err: $num.cgi");
	eval "flock(TMP, 2);";
	print TMP "$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pwd<>$time<>";
	close(TMP);

	chmod(0666,"$cf{logdir}/$num.cgi");
}

#-----------------------------------------------------------
#  mime�G���R�[�h
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


