.PHONY: help preview render aboutme clean check

help:
	@echo "Targets:"
	@echo "  make preview   Render once, then start the live preview server"
	@echo "  make render    Build the site to _site/ and exit"
	@echo "  make aboutme   Fetch the GitHub profile README into assets/_aboutme.md"
	@echo "  make clean     Remove build outputs (_site/, .quarto/, assets/_aboutme.md)"
	@echo "  make check     Run quarto check for environment diagnostics"

aboutme:
	./scripts/fetch-aboutme.sh

preview: aboutme
	quarto render && quarto preview

render: aboutme
	quarto render

clean:
	rm -rf _site .quarto assets/_aboutme.md

check:
	quarto check
