import json
import re
import pandas as pd
import numpy as np
from collections import namedtuple

n_sketches_created = 14542
n_sketches_hearted = 14196
n_sketches_total = n_sketches_created + n_sketches_hearted


### CLOC ###

def load_cloc(filename):
    data = pd.read_csv(filename, index_col='language')
    return data


def write_csv(filename, dataframe):
    dataframe.to_csv(filename)


def anylise_cloc(filecreated, filehearted, language):

    df_created = load_cloc(filecreated)
    df_hearted = load_cloc(filehearted)

    # created
    tot_created = df_created.loc['SUM']['files']
    n_files_created = df_created.loc[language]['files']
    loc_created = df_created.loc[language]['code']
    lo_comms_created = df_created.loc[language]['comment']

    loc_per_file_created = round(loc_created/n_files_created, 2)
    lo_comms_per_file_created = round(lo_comms_created/n_files_created, 2)
    percent_files_created = round(
        (int(n_files_created) / int(tot_created)) * 100, 2)

    # hearted
    tot_hearted = df_hearted.loc['SUM']['files']
    n_files_hearted = df_hearted.loc[language]['files']
    loc_hearted = df_hearted.loc[language]['code']
    lo_comms_hearted = df_hearted.loc[language]['comment']

    loc_per_file_hearted = round(loc_hearted/n_files_hearted, 2)
    lo_comms_per_file_hearted = round(lo_comms_hearted/n_files_hearted, 2)
    percent_files_hearted = round(
        (int(n_files_hearted) / int(tot_hearted)) * 100, 2)

    # agregated
    tot = tot_created + tot_hearted
    n_files_lang = n_files_created + n_files_hearted
    loc = loc_created + loc_hearted
    lo_comms = lo_comms_created + lo_comms_hearted

    loc_per_file = round(loc/n_files_lang, 2)
    lo_comms_per_file = round(lo_comms/n_files_lang, 2)
    percent_files = round((int(n_files_lang) / int(tot)) * 100, 2)

    data = [
        {'total files': tot_created,
         f'{language} files': n_files_created,
         f'% {language} files': percent_files_created,
         f'avg {language} files per sketch': n_files_created/n_sketches_created,
         f'total loc {language}': loc_created,
         'avg loc per file': loc_per_file_created,
         f'total comments {language}': lo_comms_created,
         'avg comments per file': lo_comms_per_file_created},

        {'total files': tot_hearted,
         f'{language} files': n_files_hearted,
         f'% {language} files': percent_files_hearted,
         f'avg {language} files per sketch': n_files_hearted/n_sketches_hearted,
         f'total loc {language}': loc_hearted,
         'avg loc per file': loc_per_file_hearted,
         f'total comments {language}': lo_comms_hearted,
         'avg comments per file': lo_comms_per_file_hearted},

        {'total files': tot,
         f'{language} files': n_files_lang,
         f'% {language} files': percent_files,
         f'avg {language} files per sketch': n_files_lang/n_sketches_total,
         f'total loc {language}': loc,
         'avg loc per file': loc_per_file,
         f'total comments {language}': lo_comms,
         'avg comments per file': lo_comms_per_file}
    ]

    # Lists of dictionaries and row index.
    df = pd.DataFrame(data, index=['created', 'hearted', 'total'])
    df.index.name = 'Group'

    write_csv(f'./analysis/cloc_analysis_{language}.csv', df)


# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'JavaScript')
# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'Arduino Sketch')
# anylise_cloc("./analysis/cloc_created_skip_unique.csv",
#              "./analysis/cloc_hearted_skip_unique.csv", 'HTML')


### CR - REPORT ###

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
        file.write(json.dumps(dict, default=json_serializer, indent=2))


# sketches, files, funcs: names and counts - loc #
def get_cr_stats(data):
    reports = data["reports"]

    stats = {
        "files_setup_draw": 0,   # count files that have setup+draw funcs  --  done
        "funcs_setup": 0,           # count total of "setup" funcs  --  done
        "funcs_draw": 0,            # count total of "draw" funcs  --  done
        "n_files": len(reports),    # count all files -- done
        # [[sketchname,func["name"],func["params"],func["sloc"]["logical"]]] -- done
        "funcs": [],
        "sketches": set(),          # unique sketches -- done
        "files_names": set(),       # unique file names -- done
        "func_names": set(),        # unique functions names  --  done
        # {sketch: [[filename, sloc, [name of funcs]]]} -- done
        "files": {},
        "params": data["params"],
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


# cyclomatic - cyclomaticDensity - maintainability - halstead #
def get_cr_metrics(data):
    reports = data["reports"]

    stats = {
        # whole thing
        "n_modules": len(reports),
        "n_funcs": 0,
        "maintainability_mod_avg": data["maintainability"],  # avg per-module maintainability index
        "cyclomatic_func_avg": data["cyclomatic"],           # avg per-func cyclomatic complexity
        "effort_func_avg": data["effort"],                   # avg per-func Halstead effort

        # per report (aggregate or out)
        "maintainability_mod_list": [],      # maintainability index for the module
        "cyclomatic_mod_list": [],           # agg -> cyclomatic complex for the module
        "cyclomaticDensity_mod_list": [],    # agg -> cyclomatic complex density for the module
        "effort_mod_func_avg_list": [],      # avg of Halstead effort of funcs in module
        "cyclomatic_mod_func_avg_list": [],  # avg of cyclomatic complex of funcs in module

        # per func in report
        "cyclomatic_func_list": [],         # cyclomatic complex for the func
        "cyclomaticDensity_func_list": [],  # cyclomatic complex density for the func

        # halstead
        # aggregate -- for the module
        "vocabulary_mod_list": [],  # Halstead vocabulary size
        "difficulty_mod_list": [],  # Halstead difficulty
        "volume_mod_list": [],  # Halstead volume
        "effort_mod_list": [],  # Halstead effort
        "bugs_mod_list": [],  # Halstead bugs
        "time_mod_list": [],  # Halstead time

        # func -- for the func
        "vocabulary_func_list": [],  # Halstead vocabulary size
        "difficulty_func_list": [],  # Halstead difficulty
        "volume_func_list": [],  # Halstead volume
        "effort_func_list": [],  # Halstead effort
        "bugs_func_list": [],  # Halstead bugs
        "time_func_list": [],  # Halstead time
    }

    for report in reports:
        stats["maintainability_mod_list"].append(report["maintainability"])
        stats["cyclomatic_mod_list"].append(report["aggregate"]["cyclomatic"])
        stats["cyclomaticDensity_mod_list"].append(report["aggregate"]["cyclomaticDensity"])
        stats["effort_mod_func_avg_list"].append(report["effort"])
        stats["cyclomatic_mod_func_avg_list"].append(report["cyclomatic"])

        stats["vocabulary_mod_list"].append(report["aggregate"]["halstead"]["vocabulary"])
        stats["difficulty_mod_list"].append(report["aggregate"]["halstead"]["difficulty"])
        stats["volume_mod_list"].append(report["aggregate"]["halstead"]["volume"])
        stats["effort_mod_list"].append(report["aggregate"]["halstead"]["effort"])
        stats["bugs_mod_list"].append(report["aggregate"]["halstead"]["bugs"])
        stats["time_mod_list"].append(report["aggregate"]["halstead"]["time"])

        for func in report["functions"]:
            stats["n_funcs"] += 1
            stats["cyclomatic_func_list"].append(func["cyclomatic"])
            stats["cyclomaticDensity_func_list"].append(func["cyclomaticDensity"])

            stats["vocabulary_func_list"].append(func["halstead"]["vocabulary"])
            stats["difficulty_func_list"].append(func["halstead"]["difficulty"])
            stats["volume_func_list"].append(func["halstead"]["volume"])
            stats["effort_func_list"].append(func["halstead"]["effort"])
            stats["bugs_func_list"].append(func["halstead"]["bugs"])
            stats["time_func_list"].append(func["halstead"]["time"])

    return stats


def join_cr_stats(s1, s2):

    joined_dict = {
        # add count of both stat_dicts
        "files_setup_draw": s1["files_setup_draw"] + s2["files_setup_draw"],
        # add count of both stat_dicts
        "funcs_setup": s1["funcs_setup"] + s2["funcs_setup"],
        # add count of both stat_dicts
        "funcs_draw": s1["funcs_draw"] + s2["funcs_draw"],
        # add count of both stat_dicts
        "n_files": s1["n_files"] + s2["n_files"],
        # concat list of lists
        "funcs": s1["funcs"] + s2["funcs"],
        # union sets of unique sketches
        "sketches": s1["sketches"].union(s2["sketches"]),
        # union sets of unique file names
        "files_names": s1["files_names"].union(s2["files_names"]),
        # union sets of unique functions names
        "func_names": s1["func_names"].union(s2["func_names"]),
        # {sketch: [[filename, sloc, [name of funcs]]]} -- done
        "files": {**s1["files"], **s2["files"]},
        "sloc_logical": {'max': max(s1["sloc_logical"]["max"], s2["sloc_logical"]["max"]),  # max of both stat_dicts
                         # min of both stat_dicts
                         'min': min(s1["sloc_logical"]["min"], s2["sloc_logical"]["min"]),
                         # sum of both stat_dicts
                         'sum': s1["sloc_logical"]["sum"] + s2["sloc_logical"]["sum"],
                         'file_avg': 0,
                         'func_avg': 0}
    }

    joined_dict["sloc_logical"]["file_avg"] = joined_dict["sloc_logical"]["sum"] / \
        joined_dict["n_files"]

    # (avg1 * count1, avg2 *coun2) / (count1+count2)
    sum1 = s1["sloc_logical"]["func_avg"] * len(s1["funcs"])
    sum2 = s2["sloc_logical"]["func_avg"] * len(s2["funcs"])
    total_funcs = len(s1["funcs"]) + len(s2["funcs"])
    joined_dict["sloc_logical"]["func_avg"] = (sum1 + sum2) / total_funcs

    return joined_dict


def join_cr_metrics(m1, m2):

    joined_dict = {
        "n_modules": m1["n_modules"] + m2["n_modules"],
        "n_funcs": m1["n_funcs"] + m2["n_funcs"],
        "maintainability_mod_avg": 0,  # avg per-module maintainability index
        "cyclomatic_func_avg": 0,      # avg per-func cyclomatic complexity
        "effort_func_avg": 0,          # avg per-func Halstead effort

        # per report (aggregate or out)
        "maintainability_mod_list": [*m1["maintainability_mod_list"], *m2["maintainability_mod_list"]],      # maintainability index for the module
        "cyclomatic_mod_list": [*m1["cyclomatic_mod_list"], *m2["cyclomatic_mod_list"]],           # agg -> cyclomatic complex for the module
        "cyclomaticDensity_mod_list": [*m1["cyclomaticDensity_mod_list"], *m2["cyclomaticDensity_mod_list"]],    # agg -> cyclomatic complex density for the module
        "effort_mod_func_avg_list": [*m1["effort_mod_func_avg_list"], *m2["effort_mod_func_avg_list"]],      # avg of Halstead effort of funcs in module
        "cyclomatic_mod_func_avg_list": [*m1["cyclomatic_mod_func_avg_list"], *m2["cyclomatic_mod_func_avg_list"]],  # avg of cyclomatic complex of funcs in module

        # per func in report
        "cyclomatic_func_list": [*m1["cyclomatic_func_list"], *m2["cyclomatic_func_list"]],         # cyclomatic complex for the func
        "cyclomaticDensity_func_list": [*m1["cyclomaticDensity_func_list"], *m2["cyclomaticDensity_func_list"]],  # cyclomatic complex density for the func

        # halstead
        # aggregate -- for the module
        "vocabulary_mod_list": [*m1["vocabulary_mod_list"], *m2["vocabulary_mod_list"]],  # Halstead vocabulary size
        "difficulty_mod_list": [*m1["difficulty_mod_list"], *m2["difficulty_mod_list"]],  # Halstead difficulty
        "volume_mod_list": [*m1["volume_mod_list"], *m2["volume_mod_list"]],  # Halstead volume
        "effort_mod_list": [*m1["effort_mod_list"], *m2["effort_mod_list"]],  # Halstead effort
        "bugs_mod_list": [*m1["bugs_mod_list"], *m2["bugs_mod_list"]],  # Halstead bugs
        "time_mod_list": [*m1["time_mod_list"], *m2["time_mod_list"]],  # Halstead time

        # func -- for the func
        "vocabulary_func_list": [*m1["vocabulary_func_list"], *m2["vocabulary_func_list"]],  # Halstead vocabulary size
        "difficulty_func_list": [*m1["difficulty_func_list"], *m2["difficulty_func_list"]],  # Halstead difficulty
        "volume_func_list": [*m1["volume_func_list"], *m2["volume_func_list"]],  # Halstead volume
        "effort_func_list": [*m1["effort_func_list"], *m2["effort_func_list"]],  # Halstead effort
        "bugs_func_list": [*m1["bugs_func_list"], *m2["bugs_func_list"]],  # Halstead bugs
        "time_func_list": [*m1["time_func_list"], *m2["time_func_list"]],  # Halstead time

    }

    joined_dict["maintainability_mod_avg"] = ((m1["maintainability_mod_avg"]*m1["n_modules"]) + (m2["maintainability_mod_avg"]*m2["n_modules"])) / joined_dict["n_modules"]
    joined_dict["cyclomatic_func_avg"] = ((m1["cyclomatic_func_avg"]*m1["n_funcs"]) + (m2["cyclomatic_func_avg"]*m2["n_funcs"])) / joined_dict["n_funcs"]
    joined_dict["effort_func_avg"] = ((m1["effort_func_avg"]*m1["n_funcs"]) + (m2["effort_func_avg"]*m2["n_funcs"]))/ joined_dict["n_funcs"]

    return joined_dict


## Load cr_reports
# df_demo = load_json("../cr_report_demo.json")  # 6  --- len(df["reports"])
# df_demo2 = load_json("../cr_report_demo_2.json")  # 7  --- len(df["reports"])
df_created1 = load_json("../cr_report_created_half1.json")  # 6010
df_created2 = load_json("../cr_report_created_half2.json")  # 6112
df_hearted1 = load_json("../cr_report_hearted_half1.json")  # 3311
df_hearted2 = load_json("../cr_report_hearted_half2.json")  # 8341


# stats = get_cr_stats_stats(df_demo)
# stats2 = get_cr_stats_stats(df_demo2)
# stats_created1 = get_cr_stats_stats(df_created1)
# stats_created2 = get_cr_stats_stats(df_created2)

# metrics = get_cr_metrics(df_demo)
# metrics2 = get_cr_metrics(df_demo2)

# print(metrics)

## Stats
# stats_created1 = get_cr_stats(df_created1)
# stats_created2 = get_cr_stats(df_created2)

# stats_hearted1 = get_cr_stats(df_hearted1)
# stats_hearted2 = get_cr_stats(df_hearted2)

# stats_created_joined = join_cr_stats(stats_created1, stats_created2)
# stats_hearted_joined = join_cr_stats(stats_hearted1, stats_hearted2)
# write_dict(stats_created_joined, "./analysis/cr/stats_created_joined.json")
# write_dict(stats_hearted_joined, "./analysis/cr/stats_hearted_joined.json")

# stats_total_joined = join_cr_stats(stats_created_joined, stats_hearted_joined)
# write_dict(stats_total_joined, "./analysis/cr/stats_total_joined.json")


## Metrics
# metrics_created1 = get_cr_metrics(df_created1)
# metrics_created2 = get_cr_metrics(df_created2)

# metrics_hearted1 = get_cr_metrics(df_hearted1)
# metrics_hearted2 = get_cr_metrics(df_hearted2)

# metrics_created_joined = join_cr_metrics(metrics_created1, metrics_created2)
# metrics_hearted_joined = join_cr_metrics(metrics_hearted1, metrics_hearted2)
# write_dict(metrics_created_joined, "./analysis/cr/metrics_created_joined.json")
# write_dict(metrics_hearted_joined, "./analysis/cr/metrics_hearted_joined.json")

# metrics_total_joined = join_cr_metrics(metrics_created_joined, metrics_hearted_joined)
# write_dict(metrics_total_joined, "./analysis/cr/metrics_total_joined.json")


def analyse_cr_stats(stats):
    # get loc's (max, min, sum for avg) ---->  get how many close to it
    # how many funcs per project, max, min, avg
    # get highest and lowest of indexes
    #
    pass


# named tuple for max min mean
MaxMinMean = namedtuple('MaxMinMean', ['max', 'min', 'mean'])


def analyse_cr_metrics(metrics):
    # get highest, lowest and avg of metrics
    max_min_mean = {}

    for key, value in metrics.items():
        if type(value) == list:
            # IGNORING Nones, only happens in cyclomaticDensity, when func has no lines, hence division by 0
            max_val = max(filter(lambda x: x is not None, value))
            min_val = min(filter(lambda x: x is not None, value))
            mean = np.mean(list(filter(lambda x: x is not None, value)))

            max_min_mean[key] = MaxMinMean(max_val, min_val, mean)

    # from avg ---->  get how many close to it

    return max_min_mean


# analyse_cr_metrics(metrics)

# df = pd.DataFrame(stats)
# print(df)
