###
###   Download busybox-static and extract busybox static bin
###

#DEB_MIRROR=http://idefix.eup.uva.es/debian/

DEB_MIRROR=http://ftp.uk.debian.org/debian/
BUSYBOX_FILE=$(shell apt-cache show busybox-static|awk '/^Filename/ {print $$2}'| head -1)

all: clean get uncompress
	@make clean

clean:
	@rm -rf *deb* *html* tmp/

dist-clean:
	@rm -f busybox

get:
	@echo Downloading $(BUSYBOX_FILE)
	@wget -q $(DEB_MIRROR)$(BUSYBOX_FILE)

uncompress: clean dist-clean
	@echo "Extracting busybox from deb file"
	@mkdir -p tmp/data
	@cd tmp/ && ar -x ../*.deb
	@cd tmp/data && tar -zxf ../data.tar.gz
	@cp `find tmp/data/ -type f  -name "busybox"` .


