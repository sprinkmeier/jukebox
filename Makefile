MDs  =$(wildcard *.md)
HTMLs=$(MDs:.md=.html)
PDFs =$(HTMLs:.html=.pdf)

CGI  =/usr/lib/cgi-bin/jukebox.cgi

DOC  =$(HTMLs) $(PDFs)

default: $(DOC) $(CGI)

$(CGI): jukebox.cgi
	sudo cp --update --verbose $^ $@

%.pdf: %.html
	html2ps < $^ | ps2pdf - > $@

%.html: %.md
	markdown $^ > $@

remake: clean
	$(MAKE)

clean:
	-rm $(DOC)

.PHONY: default remake clean
