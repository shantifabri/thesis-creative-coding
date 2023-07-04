import json
import re
import pandas as pd
from collections import Counter

n_sketches_created = 14542
n_sketches_hearted = 14196
n_sketches_total = n_sketches_created + n_sketches_hearted


def write_csv(filename, dataframe):
    dataframe.to_csv(filename)


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


# ############ #
# ### CLOC ### #
# ############ #

def load_cloc(filename):
    data = pd.read_csv(filename, index_col='language')
    return data


def analyse_cloc(filecreated, filehearted, language):

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

    write_csv(f'./analysis/cloc/cloc_analysis_{language}.csv', df)


# ############### #
# ## CR REPORT ## #
# ############### #

# sketches, files, funcs: names and counts - loc #
def get_cr_stats(data):
    reports = data["reports"]

    stats = {
        "files_setup_draw": 0,      # count files that have setup+draw funcs
        "funcs_setup": 0,           # count total of "setup" funcs
        "funcs_draw": 0,            # count total of "draw" funcs
        "n_files": 0,               # count all files
        "sketches_names": set(),    # unique sketches
        "files_names": set(),       # unique file names
        "func_names": set(),        # unique functions names
        "sketches": {},             # {sketch: [[filename, sloc, [name of funcs]]]}
        "funcs": [],                # [[func_name,func_params,func_sloc_logical,func_sloc_physical]]
    }

    # each report represents a file
    for report in reports:
        if 'p5' in report["path"]:
            continue

        stats["n_files"] += 1

        txt = report["path"]

        match = re.search(r'sketch\d+', txt)
        s, e = match.span()

        sketchname = txt[s:e]
        filename = txt[e+1:]

        stats["sketches_names"].add(sketchname)  # add sketch name
        stats["files_names"].add(filename)  # add file name

        # file SLOC
        sloc_log_file = report["aggregate"]["sloc"]["logical"]

        # file gral info
        if sketchname in stats["sketches"]:
            stats["sketches"][sketchname].append([filename, sloc_log_file, []])
        else:
            stats["sketches"][sketchname] = [[filename, sloc_log_file, []]]

        # funcs info
        draw, setup = 0, 0
        for func in report["functions"]:
            func_name = func["name"]
            stats["sketches"][sketchname][-1][-1].append(func_name)
            stats["func_names"].add(func_name)
            stats["funcs"].append(
                [func_name, func["params"], func["sloc"]["logical"], func["sloc"]["physical"]])

            if func_name == "draw":
                draw = 1
                stats["funcs_draw"] += 1

            elif func_name == "setup":
                setup = 1
                stats["funcs_setup"] += 1

        if draw and setup:
            stats["files_setup_draw"] += 1

    return stats


# loc physical - loc logical - params -- per mod and per func #
def get_cr_loc_param(data):
    reports = data["reports"]

    stats = {
        "n_modules": 0,
        "n_funcs": 0,

        "sloc_physical_mod_list": [],  # physical lines of code for the module
        "sloc_logical_mod_list": [],  # logical lines of code for the module
        "param_mod_list": [],  # parameter count for the module

        "sloc_physical_func_list": [],  # physical lines of code for the func
        "sloc_logical_func_list": [],  # logical lines of code for the func
        "param_func_list": []  # parameter count for the function.
    }

    for report in reports:
        if 'p5' in report["path"]:
            continue

        stats["n_modules"] += 1
        stats["sloc_physical_mod_list"].append(report["aggregate"]["sloc"]["physical"])
        stats["sloc_logical_mod_list"].append(report["aggregate"]["sloc"]["logical"])
        stats["param_mod_list"].append(report["aggregate"]["params"])

        for func in report["functions"]:
            stats["n_funcs"] += 1
            stats["sloc_physical_func_list"].append(func["sloc"]["physical"])
            stats["sloc_logical_func_list"].append(func["sloc"]["logical"])
            stats["param_func_list"].append(func["params"])

    return stats


# cyclomatic - cyclomaticDensity - maintainability - halstead #
def get_cr_metrics(data):
    reports = data["reports"]

    stats = {
        # whole thing
        "n_modules": 0,
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
        "length_mod_list": [],  # Halstead length size
        "vocabulary_mod_list": [],  # Halstead vocabulary size
        "difficulty_mod_list": [],  # Halstead difficulty
        "volume_mod_list": [],  # Halstead volume
        "effort_mod_list": [],  # Halstead effort
        "bugs_mod_list": [],  # Halstead bugs
        "time_mod_list": [],  # Halstead time

        # func -- for the func
        "length_func_list": [],  # Halstead length size
        "vocabulary_func_list": [],  # Halstead vocabulary size
        "difficulty_func_list": [],  # Halstead difficulty
        "volume_func_list": [],  # Halstead volume
        "effort_func_list": [],  # Halstead effort
        "bugs_func_list": [],  # Halstead bugs
        "time_func_list": [],  # Halstead time
    }

    for report in reports:
        if 'p5' in report["path"]:
            continue

        stats["n_modules"] += 1
        stats["maintainability_mod_list"].append(report["maintainability"])
        stats["cyclomatic_mod_list"].append(report["aggregate"]["cyclomatic"])
        stats["cyclomaticDensity_mod_list"].append(report["aggregate"]["cyclomaticDensity"])
        stats["effort_mod_func_avg_list"].append(report["effort"])
        stats["cyclomatic_mod_func_avg_list"].append(report["cyclomatic"])

        stats["length_mod_list"].append(report["aggregate"]["halstead"]["length"])
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

            stats["length_func_list"].append(func["halstead"]["length"])
            stats["vocabulary_func_list"].append(func["halstead"]["vocabulary"])
            stats["difficulty_func_list"].append(func["halstead"]["difficulty"])
            stats["volume_func_list"].append(func["halstead"]["volume"])
            stats["effort_func_list"].append(func["halstead"]["effort"])
            stats["bugs_func_list"].append(func["halstead"]["bugs"])
            stats["time_func_list"].append(func["halstead"]["time"])

    return stats


def join_cr_stats(s1, s2):

    joined_dict = {
        "files_setup_draw": s1["files_setup_draw"] + s2["files_setup_draw"],  # add count of both stat_dicts
        "funcs_setup": s1["funcs_setup"] + s2["funcs_setup"],  # add count of both stat_dicts
        "funcs_draw": s1["funcs_draw"] + s2["funcs_draw"],  # add count of both stat_dicts
        "n_files": s1["n_files"] + s2["n_files"],  # add count of both stat_dicts
        "sketches_names": s1["sketches_names"].union(s2["sketches_names"]),  # union sets of unique sketches
        "files_names": s1["files_names"].union(s2["files_names"]),  # union sets of unique file names
        "func_names": s1["func_names"].union(s2["func_names"]),  # union sets of unique functions names
        "sketches": {**s1["sketches"], **s2["sketches"]},  # {sketch: [[filename, sloc, [name of funcs]]]}
        "funcs": s1["funcs"] + s2["funcs"],  # concat list of lists
    }

    return joined_dict


def join_cr_loc_param(l1, l2):

    joined_dict = {
        "n_modules": l1["n_modules"] + l2["n_modules"],
        "n_funcs": l1["n_funcs"] + l2["n_funcs"],
        "sloc_physical_mod_list": [*l1["sloc_physical_mod_list"], *l2["sloc_physical_mod_list"]],
        "sloc_logical_mod_list": [*l1["sloc_logical_mod_list"], *l2["sloc_logical_mod_list"]],
        "param_mod_list": [*l1["param_mod_list"], *l2["param_mod_list"]],

        "sloc_physical_func_list": [*l1["sloc_physical_func_list"], *l2["sloc_physical_func_list"]],
        "sloc_logical_func_list": [*l1["sloc_logical_func_list"], *l2["sloc_logical_func_list"]],
        "param_func_list": [*l1["param_func_list"], *l2["param_func_list"]]
    }

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
        "length_mod_list": [*m1["length_mod_list"], *m2["length_mod_list"]],  # Halstead length size
        "vocabulary_mod_list": [*m1["vocabulary_mod_list"], *m2["vocabulary_mod_list"]],  # Halstead vocabulary size
        "difficulty_mod_list": [*m1["difficulty_mod_list"], *m2["difficulty_mod_list"]],  # Halstead difficulty
        "volume_mod_list": [*m1["volume_mod_list"], *m2["volume_mod_list"]],  # Halstead volume
        "effort_mod_list": [*m1["effort_mod_list"], *m2["effort_mod_list"]],  # Halstead effort
        "bugs_mod_list": [*m1["bugs_mod_list"], *m2["bugs_mod_list"]],  # Halstead bugs
        "time_mod_list": [*m1["time_mod_list"], *m2["time_mod_list"]],  # Halstead time

        # func -- for the func
        "length_func_list": [*m1["length_func_list"], *m2["length_func_list"]],  # Halstead length size
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


def analyse_cr_stats(stats, filename):

    # stats["sketches"] -> {sketch: [[filename, sloc, [name of funcs]]]}
    counts = {
        "funcs_per_project": [],
        "funcs_per_file": [],
        "files_per_project": [],
    }

    for key, value in stats["sketches"].items():
        project_func_count = 0
        for file in value:
            n_funcs_file = len(file[2])
            project_func_count += n_funcs_file
            counts["funcs_per_file"].append(n_funcs_file)

        counts["funcs_per_project"].append(project_func_count)
        counts["files_per_project"].append(len(value))

    write_dict(counts, "./analysis/cr/jsons/"+filename+"_project_file_func_count.json")

    # stats["funcs"] -> [[func_name,func_params,func_sloc_logical,func_sloc_physical]]
    funcs_draw_setup = {
        "params_draw": [func[1] for func in stats["funcs"] if func[0] == "draw"],
        "loc_logical_draw": [func[2] for func in stats["funcs"] if func[0] == "draw"],
        "loc_physical_draw": [func[3] for func in stats["funcs"] if func[0] == "draw"],
        "params_setup": [func[1] for func in stats["funcs"] if func[0] == "setup"],
        "loc_logical_setup": [func[2] for func in stats["funcs"] if func[0] == "setup"],
        "loc_physical_setup": [func[3] for func in stats["funcs"] if func[0] == "setup"]
    }

    write_dict(funcs_draw_setup, "./analysis/cr/jsons/"+filename+"_setup_draw_characterization.json")

    name_counts = Counter((func[0] for func in stats["funcs"]))

    func_name_counters = {
        "name_counts": name_counts,
    }

    write_dict(func_name_counters, "./analysis/cr/jsons/"+filename+"_func_name_counters.json")


def analyse_cr_loc_param(loc_param, filename):
    module_loc_param = {}
    func_loc_param = {}

    for key, value in loc_param.items():
        if type(value) == list:
            if len(value) == loc_param["n_modules"]:
                module_loc_param[key] = value

            elif len(value) == loc_param["n_funcs"]:
                func_loc_param[key] = value

    module_dataframe = pd.DataFrame.from_dict(module_loc_param)
    func_dataframe = pd.DataFrame.from_dict(func_loc_param)

    write_csv("./analysis/cr/csvs/"+filename+"_loc_param_module.csv", module_dataframe)
    write_csv("./analysis/cr/csvs/"+filename+"_loc_param_func.csv", func_dataframe)


def analyse_cr_metrics(metrics, filename):
    module_metrics = {}
    func_metrics = {}

    for key, value in metrics.items():
        if type(value) == list:
            if len(value) == metrics["n_modules"]:
                module_metrics[key] = value

            elif len(value) == metrics["n_funcs"]:
                func_metrics[key] = value

    module_dataframe = pd.DataFrame.from_dict(module_metrics)
    func_dataframe = pd.DataFrame.from_dict(func_metrics)

    write_csv("./analysis/cr/csvs/"+filename+"_metrics_module.csv", module_dataframe)
    write_csv("./analysis/cr/csvs/"+filename+"_metrics_func.csv", func_dataframe)


# # Load cr_reports
# df_demo = load_json("../cr_report_demo.json")  # 6  --- len(df["reports"])
# df_demo2 = load_json("../cr_report_demo_2.json")  # 7


# stats
# stats_demo = get_cr_stats(df_demo)
# stats_demo2 = get_cr_stats(df_demo2)

# write_dict(stats_demo, "stats_demo.json")
# write_dict(stats_demo2, "stats_demo2.json")

# join_stats_demo = (join_cr_stats(stats_demo, stats_demo2))

# write_dict(join_stats_demo, "stats_joined_demo.json")

# analyse_cr_stats(stats_demo, "demo")


# # metrics
# metrics_demo = get_cr_metrics(df_demo)
# metrics_demo2 = get_cr_metrics(df_demo2)
# df_hearted2 = load_json("../cr_report_created_half2.json")  # 8341
# df_hearted = load_json("../cr_report_created_half1.json")  # 8341

# metrics_hearted2 = get_cr_metrics(df_hearted2)
# metrics_hearted2 = get_cr_metrics(df_hearted)

# analyse_cr_metrics(metrics_demo, "demo")


# # loc_param
# loc_param_demo = get_cr_loc_param(df_demo)
# loc_param_demo = get_cr_loc_param(df_demo2)

# analyse_cr_loc_param(loc_param_demo, "demo")
