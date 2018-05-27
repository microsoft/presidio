# Looks at a stream line by line and finds duplicates or incorrect alphabetization.
my $prev = <STDIN>;
my $exitStatus = 0;
while(my $current = <STDIN>) {
    if($current le $prev ){
        print STDERR $current;
        $exitStatus = 1;
    }
    $prev = $current
}
exit $exitStatus;