from typing import Pattern
from bs4 import BeautifulSoup
import re
import requests
import logging

logging.basicConfig(level=logging.ERROR)


class Searcher():
    def __init__(self, querries: list[str], sites: list[str], range: int):
        self.querries = querries
        self.texts: dict[str, str] = dict()
        # findings :
        #   url:
        #       { querry:
        #              set(finings)
        #       }
        self.findings: dict[str, dict[str, set]] = dict()
        self.sites = sites
        self.range: int = range
        # possible more patterns in the process
        self.patterns: dict[str, Pattern] = dict()
        for querry in self.querries:
            self.patterns[querry] = re.compile(
                r".{0," + re.escape(str(self.range)) + r"}"
                + re.escape(querry) + r".{0,"
                + re.escape(str(self.range)) + r"}",
                re.IGNORECASE)
        # get the site contents
        self._get_text()
        logging.info("search string", self.querries, "texts",
                     self.texts, "pattern", self.patterns)

    def _get_text(self):
        for site in self.sites:
            response = requests.get(site)
            self.texts[site] = BeautifulSoup(
                response.text, "html.parser").get_text()

    def results(self):
        for key, text in self.texts.items():
            self.findings[key] = dict()
            for querry, pattern in self.patterns.items():
                findingsList = re.findall(pattern, text)
                self.findings[key][querry] = set(findingsList)
                logging.info(findingsList)
        return self.findings

    def pretty_print(self, header: str) -> str:
        """Print the findings in a markdown format

        This function prints the findings in a markdown format so that
        the user is able to read them in a structured way and knows which
        finding belongs to which site.

        Args
        ----
        header: str 
            the header for the hole markdown file

        Returns
        -------
        md: str
            markdown string output that can we written to the terminal
            or can be piped into a markdown file
        """
        md: str = f"# {header}\n\n"
        for site, finding in self.findings.items():
            header = self._print_header(site)
            body = self._print_findings(finding)
            md += f"{header}{body}\n\n"
        return md

    def _print_header(self, site: str) -> str:
        return f"## {site}\n"

    def _print_findings(self, finding: dict[str, set]) -> str:
        res: str = ""
        header = False
        if len(finding.keys()) > 1:
            header = True
            res += "\n\nHere are all findings for the querries\n"
        else:
            res += "\n\nHere are all findings for the querry\n"
        for key, findings in finding.items():
            if header:
                res += "\n### " + key + "\n"
            for i, sentence in enumerate(findings):
                res += f"\n{i + 1}. {sentence}"
            if len(findings) > 0:
                res += "\n"
        return res
