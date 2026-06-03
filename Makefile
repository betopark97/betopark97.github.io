.PHONY: help preview render clean check

help:
	@echo "Targets:"
	@echo "  make preview   Render once, then start the live preview server"
	@echo "  make render    Build the site to _site/ and exit"
	@echo "  make clean     Remove build outputs (_site/, .quarto/)"
	@echo "  make check     Run quarto check for environment diagnostics"

preview:
	quarto render && quarto preview

render:
	quarto render

clean:
	rm -rf _site .quarto

check:
	quarto check
