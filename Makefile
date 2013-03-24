MDs  =$(wildcard *.md)
HTMLs=$(MDs:.md=.html)
PSs  =$(HTMLs:.html=.ps)
PDFs =$(PSs:.ps=.pdf)

ALL  =$(HTMLs) $(PSs) $(PDFs)

CGI  =/usr/lib/cgi-bin/jukebox.cgi

default: $(ALL) $(CGI)

$(CGI): jukebox.cgi
	sudo cp --update --verbose $^ $@

%.pdf: %.ps
	$(shell ps2pdf $^ $@ || rm $^ ; false )

%.ps: %.html
	$(shell html2ps < $^ > $@ || rm $^ ; false )

%.html: %.md
	$(shell markdown $^ > $@ || rm $^ ; false )

remake: clean
	$(MAKE)

clean:
	-rm $(ALL)

.PHONY: default remake clean
