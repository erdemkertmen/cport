"""META-PPISP module."""
# This predictor takes around 2 hours to complete,
# so should be first to be examined if the output
# increases accuracy of CPORT, if it does not
# this predictor should be scrapped
import io
import logging
import re
import sys
import tempfile
import time

import mechanicalsoup as ms
import pandas as pd
import requests

from cport.url import META_PPISP_URL

log = logging.getLogger("cportlog")

# Total wait (seconds) = WAIT_INTERVAL * NUM_RETRIES
WAIT_INTERVAL = 60  # seconds
NUM_RETRIES = 300


class MetaPPISP:
    """Meta-PPISP class."""

    def __init__(self, pdb_file, chain_id):
        """
        Initialize the class.

        Parameters
        ----------
        pdb_file : str
            Path to PDB file.
        chain_id : str
            Chain identifier.

        """
        self.pdb_file = pdb_file
        self.chain_id = chain_id
        self.prediction_dict = {}
        self.wait = WAIT_INTERVAL
        self.tries = NUM_RETRIES

    def submit(self):
        """
        Make a submission to the meta-PPISP server.

        Returns
        -------
        processing_url : str
            The url of the meta-PPISP processing page.

        """
        browser = ms.StatefulBrowser()
        # SSL request fails, try to find alternative solution as this would save
        # a lot of code
        browser.open(META_PPISP_URL, verify=False)

        input_form = browser.select_form(nr=0)
        input_form.set(name="submitter", value=str(self.chain_id))
        input_form.set(name="emailAddr", value="validmail@trustme.yes")
        input_form.set(name="pChain", value=self.chain_id)
        input_form.set(name="userfile", value=self.pdb_file)
        browser.submit_selected()

        # https://regex101.com/r/FBgZFE/1
        processing_url = re.findall(r"<a href=\"(.*)\">this link<", str(browser.page))[
            0
        ]
        log.debug(f"The url being looked at: {processing_url}")

        return processing_url

    def retrieve_prediction_link(self, url=None, page_text=None):
        """
        Retrieve the link to the meta-PPISP prediction page.

        Parameters
        ----------
        url : str
            The url of the meta-PPISP processing page.
        page_text : str
            The text of the meta-PPISP processing page.

        Returns
        -------
        url : str
            The url of the obtained meta-PPISP prediction page.

        """
        browser = ms.StatefulBrowser()

        if page_text:
            # this is used in the testing
            browser.open_fake_page(page_text=page_text)
            url = page_text
        else:
            browser.open(url, verify=False)

        completed = False
        while not completed:
            # Check if the result page exists
            match = re.search(r"404 Not Found", str(browser.page))
            if not match:
                completed = True
            else:
                # still running, wait a bit
                log.debug(f"Waiting for meta-PPISP to finish... {self.tries}")
                time.sleep(self.wait)
                browser.refresh()
                self.tries -= 1

            if self.tries == 0:
                # if tries is 0, then the server is not responding
                log.error(f"meta-PPISP server is not responding, url was {url}")
                sys.exit()

        return url

    @staticmethod
    def download_result(download_link):
        """
        Download the results.

        Parameters
        ----------
        download_link : str
            The url of the meta-PPISP result page.

        Returns
        -------
        temp_file.name : str
            The name of the temporary file containing the results.

        """
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        # this verify=False is a security issue but i'm afraid there's
        #  no trivial solution and that the issue might be of the server
        temp_file.name = requests.get(download_link, verify=False).content  # nosec
        return temp_file.name

    def parse_prediction(self, url=None, test_file=None):
        """
        Take the results extracts the active and passive residue predictions.

        Parameters
        ----------
        url : str
            The url of the meta-PPISP result page.
        test_file : str
            A file containing the text present in the result page

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the active and passive residue predictions.

        """
        prediction_dict = {"active": [], "passive": []}

        if test_file:
            final_predictions = pd.read_csv(
                test_file,
                skiprows=12,
                delim_whitespace=True,
                names=[
                    "AA",
                    "Ch",
                    "AA_nr",
                    "cons_ppisp",
                    "PINUP",
                    "Promate",
                    "meta_ppisp",
                    "Prediction",
                ],
                header=0,
                skipfooter=12,
                index_col=False,
            )
        else:
            # direct reading of page with read_csv is impossible due to the
            #  same SSL error
            file = self.download_result(url)
            final_predictions = pd.read_csv(
                io.StringIO(file.decode("utf-8")),
                skiprows=12,
                delim_whitespace=True,
                names=[
                    "AA",
                    "Ch",
                    "AA_nr",
                    "cons_ppisp",
                    "PINUP",
                    "Promate",
                    "meta_ppisp",
                    "Prediction",
                ],
                header=0,
                skipfooter=12,
                index_col=False,
            )

        for row in final_predictions.itertuples():
            if row.Prediction == "P":  # positive for interaction
                # save confidence of prediction
                # trunk-ignore(flake8/W605)
                score = [int(re.sub("\D", "", row.AA_nr)), float(row.meta_ppisp)]
                prediction_dict["active"].append(score)
            elif row.Prediction == "N":
                # trunk-ignore(flake8/W605)
                prediction_dict["passive"].append(int(re.sub("\D", "", row.AA_nr)))

        return prediction_dict

    def run(self):
        """
        Execute the meta-PPISP prediction.

        Returns
        -------
        prediction_dict : dict
            A dictionary containing the active and passive residue predictions.

        """
        log.info("Running meta-PPISP")
        log.info(f"Will try {self.tries} times waiting {self.wait}s between tries")

        submitted_url = self.submit()
        prediction_url = self.retrieve_prediction_link(url=submitted_url)
        self.prediction_dict = self.parse_prediction(url=prediction_url)

        return self.prediction_dict
