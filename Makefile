MDs  =$(wildcard *.md)
HTMLs=$(MDs:.md=.html)
PSs  =$(HTMLs:.html=.ps)
PDFs =$(PSs:.ps=.pdf)

ALL  =$(HTMLs) $(PSs) $(PDFs)

default: $(ALL)

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
