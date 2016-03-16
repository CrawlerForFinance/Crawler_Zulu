from subprocess import call
for i in xrange(1,3):
	call("Crawler_zulu.exe -tn %d" % i, shell=True)