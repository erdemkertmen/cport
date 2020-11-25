import time
from urllib import request
import requests
import os
import lxml.html
from tools import pdb, predictors

from IPython import embed

def wait_whiscy(url,temp_file):
    waiting = 0
    while True:
        html_string = request.urlopen(url).read().decode("utf-8")
        if "404 Not Found" in html_string:
            raise AssertionError("Url not found")
        if waiting > 120 * 60:
            raise Exception("Timeout on the whiscy server")
        if "[ERROR]" in html_string:
            error_message = "whiscy [ERROR] {} URL: {}".format(html_string.split("[ERROR]")[1].split("<br/>")[0],url)
            print(error_message,file=open(temp_file, "a"))
            return error_message
        if "whiscy.pdb" in html_string:
            for line in html_string.split("\n"):
                if "whiscy.pdb" in line:
                    pdb_dir = line
                    pdb_dir = pdb_dir.split('"')[-2]
                    pdb_url = 'https://wenmr.science.uu.nl' + pdb_dir
                    print("WHISCY: URL found", file=open(temp_file, "a"))
                    return pdb_url
        else:
            print("WHISCY: proccesing {}".format(waiting), file=open(temp_file, "a"))
            # print(waiting)
            # print(html_string)
        time.sleep(5)
        waiting += 5

def get_csrf_token(page):
    html = lxml.html.fromstring(page)
    hidden_elements = html.xpath('//form//input[@type="hidden"]')
    token = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}
    return token['csrf_token']


def run(input_params, main_dir):
    url = 'https://wenmr.science.uu.nl/whiscy/'

    session = requests.session()
    init_session = session.get(url, verify=False)
    csrf_token = get_csrf_token(init_session.text)
    pdb_file = open(input_params.pdb_file.pdb_dir)
    seq_file = open(input_params.seqence_file.seq_dir)

    data = {"chain": input_params.chain_id,
            "alignment_format": input_params.seqence_file.format,
            "interface_propensities": True,
            "surface_smoothing": True,
            "csrf_token": csrf_token}

    files = {"pdb_file": pdb_file,
             "alignment_file":seq_file}

    req = session.post(url, data=data, files =files)

    temp_dir = os.path.join(main_dir, "temp")
    temp_file = os.path.join(temp_dir, "whiscy.status")
    print("WHISCY: Start", file=open(temp_file, "a"))

    results_url = req.text.split('"')[-2]

    final_url = wait_whiscy(results_url,temp_file)

    if "ERROR" in final_url:
        print("WHISCY: Failed {}".format(final_url), file=open(temp_file, "a"))
        return predictors.Predictor(pdb=input_params.pdb_file, success=False)
    else:
        results_pdb = pdb.from_url(final_url, name="WHISCY", main_dir=main_dir)
        print("WHISCY: Run finished successfully", file=open(temp_file, "a"))
        return predictors.Predictor(pdb=results_pdb, success=True)
