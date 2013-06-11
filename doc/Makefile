MDs  =$(wildcard *.md)
HTMLs=$(MDs:.md=.html)
PDFs =$(HTMLs:.html=.pdf)
DOC  =$(HTMLs) $(PDFs)

default: $(DOC)

%.pdf: %.html
	html2ps < $^ | ps2pdf - > $@

%.html: %.md
	markdown $^ > $@

remake: clean
	$(MAKE)

clean:
	-rm $(DOC)

.PHONY: default remake clean
