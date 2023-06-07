import json
import re
import pandas as pd
from collections import defaultdict


def load_cloc(filename):
    data = pd.read_csv(filename, index_col='language')
    return data


def write_csv(filename, dataframe):
    dataframe.to_csv(filename)


def anylise_cloc(filecreated, filehearted, language):

    df_created = load_cloc(filecreated)
    df_hearted = load_cloc(filehearted)

    tot_created = df_created.loc['SUM']['files']
    n_files_created = df_created.loc[language]['files']
    loc_created = df_created.loc[language]['code']
    lo_comms_created = df_created.loc[language]['comment']

    loc_per_file_created = round(loc_created/n_files_created, 2)
    lo_comms_per_file_created = round(lo_comms_created/n_files_created, 2)
    percent_files_created = round(
        (int(n_files_created) / int(tot_created)) * 100, 2)

    tot_hearted = df_hearted.loc['SUM']['files']
    n_files_hearted = df_hearted.loc[language]['files']
    loc_hearted = df_hearted.loc[language]['code']
    lo_comms_hearted = df_hearted.loc[language]['comment']

    loc_per_file_hearted = round(loc_hearted/n_files_hearted, 2)
    lo_comms_per_file_hearted = round(lo_comms_hearted/n_files_hearted, 2)
    percent_files_hearted = round(
        (int(n_files_hearted) / int(tot_hearted)) * 100, 2)

    data = [{'total files': tot_created,
             f'{language} files': n_files_created,
             f'% {language} files': percent_files_created,
             f'total loc {language}': loc_created,
             'avg loc per file': loc_per_file_created,
             f'total comments {language}': lo_comms_created,
             'avg comments per file': lo_comms_per_file_created},
            {'total files': tot_hearted,
             f'{language} files': n_files_hearted,
             f'% {language} files': percent_files_hearted,
             f'total loc {language}': loc_hearted,
             'avg loc per file': loc_per_file_hearted,
             f'total comments {language}': lo_comms_hearted,
             'avg comments per file': lo_comms_per_file_hearted}]

    # Lists of dictionaries and row index.
    df = pd.DataFrame(data, index=['created', 'hearted'])

    write_csv(f'./analysis/cloc_analysis_{language}.csv', df)


# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'JavaScript')
# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'Arduino Sketch')


def load_json(filename):
    with open(filename, encoding="utf8") as f:
        data = json.load(f)
    return data


def json_serializer(value):
    if isinstance(value, set):
        return list(value)
    return value


def write_dict(dict, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(dict, default=json_serializer))


df_demo = load_json("../cr_report_demo.json")  # 6  --- len(df["reports"])
df_demo2 = load_json("../cr_report_demo_2.json")  # 7  --- len(df["reports"])
# df_created1 = load_json("../cr_report_created_half1.json")  # 6010
# df_created2 = load_json("../cr_report_created_half2.json") # 6112
# df_hearted1 = load_json("../cr_report_hearted_half1.json") # 3311
# df_hearted2 = load_json("../cr_report_hearted_half2.json") # 8341


def analyse_cr(data):
    reports = data["reports"]

    stats = {
        "files_setup_draw": 0,   # count files that have setup+draw funcs  --  done
        "funcs_setup": 0,           # count total of "setup" funcs  --  done
        "funcs_draw": 0,            # count total of "draw" funcs  --  done
        "n_files": len(reports),    # count all files -- done
        "funcs": [],                # [[sketchname,func["name"],func["params"],func["sloc"]["logical"]]]
        "sketches": set(),          # unique sketches -- done
        "files_names": set(),       # unique file names -- done
        "func_names": set(),        # unique functions names  --  done
        "files": {},                # {sketch: [[filename, sloc, [name of funcs]]]} -- done
        "sloc_logical": {'max': 0,
                         'min': 1000,
                         'sum': 0,
                         'file_avg': 0,
                         'func_avg': data["loc"]}
    }

    # each report represents a file
    for report in reports:
        txt = report["path"]

        match = re.search(r'sketch\d+', txt)
        s, e = match.span()

        sketchname = txt[s:e]
        filename = txt[e+1:]

        stats["sketches"].add(sketchname)  # add sketch name
        stats["files_names"].add(filename)  # add file name

        # file SLOC
        sloc_log_file = report["aggregate"]["sloc"]["logical"]
        stats["sloc_logical"]["sum"] += sloc_log_file

        if sloc_log_file > stats["sloc_logical"]["max"]:
            stats["sloc_logical"]["max"] = sloc_log_file

        if sloc_log_file < stats["sloc_logical"]["min"]:
            stats["sloc_logical"]["min"] = sloc_log_file

        # file gral info
        if sketchname in stats["files"]:
            stats["files"][sketchname].append([filename, sloc_log_file, []])
        else:
            stats["files"][sketchname] = [[filename, sloc_log_file, []]]

        # funcs info
        draw, setup = 0, 0
        for func in report["functions"]:
            func_name = func["name"]
            stats["files"][sketchname][-1][-1].append(func_name)
            stats["func_names"].add(func_name)
            stats["funcs"].append(
                [sketchname, func_name, func["params"], func["sloc"]["logical"]])

            if func_name == "draw":
                draw = 1
                stats["funcs_draw"] += 1

            elif func_name == "setup":
                setup = 1
                stats["funcs_setup"] += 1

        if draw and setup:
            stats["files_setup_draw"] += 1

    stats["sloc_logical"]["file_avg"] = stats["sloc_logical"]["sum"]/stats["n_files"]

    return stats

# see if paths repeat - counter of files per sketch - path up till last \\
# get highest and lowest of indexes


stats = analyse_cr(df_demo)
# stats2 = analyse_cr(df_demo2)
# stats_created1 = analyse_cr(df_created1)
# stats_created2 = analyse_cr(df_created2)


def join_cr_stats(stats1, stats2):

    joined_dict = {
        "files_setup_draw": stats1["files_setup_draw"] + stats2["files_setup_draw"],                # add count of both stat_dicts
        "funcs_setup": stats1["funcs_setup"] + stats2["funcs_setup"],                               # add count of both stat_dicts
        "funcs_draw": stats1["funcs_draw"] + stats2["funcs_draw"],                                  # add count of both stat_dicts
        "n_files": stats1["n_files"] + stats2["n_files"],                                           # add count of both stat_dicts
        "funcs": stats1["funcs"] + stats2["funcs"],                                                 # concat list of lists
        "sketches": stats1["sketches"].union(stats2["sketches"]),                                   # union sets of unique sketches
        "files_names": stats1["files_names"].union(stats2["files_names"]),                          # union sets of unique file names
        "func_names": stats1["func_names"].union(stats2["func_names"]),                             # union sets of unique functions names
        "files": {**stats1["files"], **stats2["files"]},                                            # {sketch: [[filename, sloc, [name of funcs]]]} -- done
        "sloc_logical": {'max': max(stats1["sloc_logical"]["max"], stats2["sloc_logical"]["max"]),  # max of both stat_dicts
                         'min': min(stats1["sloc_logical"]["min"], stats2["sloc_logical"]["min"]),  # min of both stat_dicts
                         'sum': stats1["sloc_logical"]["sum"] + stats2["sloc_logical"]["sum"],      #sum of both stat_dicts
                         'file_avg': 0,
                         'func_avg': 0}
    }

    joined_dict["sloc_logical"]["file_avg"] = joined_dict["sloc_logical"]["sum"] / joined_dict["n_files"]

    # (avg1 * count1, avg2 *coun2) / (count1+count2)
    sum1 = stats1["sloc_logical"]["func_avg"] * len(stats1["funcs"])
    sum2 = stats2["sloc_logical"]["func_avg"] * len(stats2["funcs"])
    total_funcs = len(stats1["funcs"]) + len(stats2["funcs"])
    joined_dict["sloc_logical"]["func_avg"] = (sum1 + sum2) / total_funcs

    return joined_dict


# s = join_cr_stats(stats, stats2)
# print(s)
# write_dict(s, "test_join.json")


def analyse_cr_stats(stats):
    # get loc's (max, min, sum for avg) ---->  get how many close to it
    # how many funcs per project, max, min, avg
    pass


# df = pd.DataFrame(stats)
# print(df)
