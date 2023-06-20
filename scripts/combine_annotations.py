import json 
import random
import os


def get_x_bbc_ids(x):
    '''
    Extracts bbc_ids and chooses x instances
    '''
    with open("./../xsum_hallucination_annotations/factuality_annotations_xsum_summaries.csv") as f:
        annotations = f.readlines()[1:]
    all_bbc_ids = []
    for annotation in annotations:
        bbc_id = annotation.split(",")[0]
        if bbc_id not in all_bbc_ids:
            all_bbc_ids.append(bbc_id)
    random.seed(42)
    random.shuffle(all_bbc_ids)
    selected = all_bbc_ids[:x] 
    leftover = all_bbc_ids[x:]
    return selected, leftover

def get_url_from_bbc_id(bbc_ids, suffix=""):
    '''
    bbc_ids: output from get_x_bbc_ids(x)
    suffix: to distinguish the selected ids from the leftovers
    Returns the url to use for querying the history machine (although in the next step i just read the file)
    '''
    with open("./XSum-Dataset/XSum-WebArxiveUrls.txt") as f:
        urls = f.readlines()
    filtered_urls = []
    url_bbc_ids = [url.strip()[-8:] for url in urls]
    for i, bbc_id in enumerate(url_bbc_ids):
        if bbc_id in bbc_ids:
            filtered_urls.append(urls[i])
    with open(f"./XSum-Dataset/XSum-WebArxiveUrls{suffix}.txt", "w") as f:
        f.writelines(filtered_urls)
    if len(bbc_ids) > len(filtered_urls):
        print("Warning: there are some annotations that don't have corresponding urls in original dataset")
    elif len(filtered_urls) > len(bbc_ids):
        print("Warning: there are some urls that don't have corresponding annotations")
    return filtered_urls

def get_data_from_urls():
    '''
    Assumes we already ran the provided script for downloading data
    Returns: dict containing text, summary, and factuality annotations
    '''
    with open("./XSum-Dataset/XSum-WebArxiveUrls_Filtered.txt") as f:
        urls = f.readlines()
        urls = [url.strip() for url in urls]
        bbc_ids = [url.strip()[-8:] for url in urls]
    # collect annotations
    data = {}
    with open("./../xsum_hallucination_annotations/factuality_annotations_xsum_summaries.csv") as f:
        annotations = f.readlines()[1:]
        for annotation in annotations:
            bbc_id = annotation.split(",")[0]
            if bbc_id in bbc_ids:
                if bbc_id not in data:
                    data[bbc_id] = {}
                    data[bbc_id]["factuality"] = []
                data[bbc_id]["factuality"].append(annotation.split(",")[-2].strip())
    print("annotations", json.dumps(data, indent=4))
    # get all files from dir
    dirname = "./XSum-Dataset/xsum-extracts-from-downloads-filtered/"
    for i, bbc_id in enumerate(bbc_ids):
        with open(os.path.join(dirname, f'{bbc_id}.data')) as f:
            content = f.readlines()
            url = urls[i]
            if url in urls:
                summary_ind = content.index("[XSUM]INTRODUCTION[XSUM]\n") + 1
                text_ind = content.index("[XSUM]RESTBODY[XSUM]\n") + 1
                summary = ' '.join(content[summary_ind:text_ind-1])
                text = ' '.join(content[text_ind:])
                data[bbc_id]["summary"] = summary
                data[bbc_id]["text"] = text
                data[bbc_id]["url"] = url
    print("data", json.dumps(data[urls[0]], indent=4))

selected, leftover = get_x_bbc_ids(20)
selected_urls = get_url_from_bbc_id(selected, "_Filtered")
leftover_urls = get_url_from_bbc_id(leftover, "_Leftover")
#get_data_from_urls()
#print(filtered_urls)

def main():
    with open("./XSum-Dataset/chosen_urls.txt", "r") as f:
        chosen_urls = f.readlines()
        bbcids = [url.split("-")[-1].strip() for url in chosen_urls]
        for i in range(len(bbcids)):
            if len(bbcids[i]) > 8:
                bbcids[i] = bbcids[i].split("/")[-1]

    selected = {}
    for category in ["factuality"]:#, "hallucination"]:
        with open(f"./../xsum_hallucination_annotations/{category}_annotations_xsum_summaries.csv", "r") as f:
            annotations = f.readlines()[1:]
            for annotation in annotations:
                bbcid = annotation.split(",")[0]
                print(bbcid, type(bbcid), type(bbcids[0]))
                if bbcid in bbcids:
                    if bbcid not in selected:
                        selected[bbcid] = []
                    selected[bbcid].append(annotation.split(",")[-2].strip())
    print(json.dumps(selected, indent=4))
    '''
    with open(f"./../xsum_hallucination_annotations/{category}_annotations_xsum_summaries.csv", "w") as f:
        f.write("bbc_id,annotation\n")
        for bbcid in bbcids:
            for annotation in annotations:
                if bbcid in annotation:
                    f.write(annotation)
                    break 
    '''

if __name__ == "__main__":
    #main()
    pass
