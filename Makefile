MDs  =$(wildcard *.md)
HTMLs=$(MDs:.md=.html)
PDFs =$(HTMLs:.html=.pdf)
DOC  =$(HTMLs) $(PDFs)

CGI  =/usr/lib/cgi-bin/jukebox.cgi

HTML =/var/www/index.html

default: $(DOC) $(CGI) $(HTML)

$(CGI): jukebox.cgi
	sudo cp --update --verbose $^ $@

$(HTML): index.html
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
