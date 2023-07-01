from analysis import load_json, write_dict, analyse_cloc
from analysis import get_cr_stats, get_cr_loc_param, get_cr_metrics
from analysis import join_cr_stats, join_cr_loc_param, join_cr_metrics
from analysis import analyse_cr_stats, analyse_cr_metrics, analyse_cr_loc_param


analyse_cloc("./analysis/cloc_created_skip_unique.csv", "./analysis/cloc_hearted_skip_unique.csv", 'JavaScript')
analyse_cloc("./analysis/cloc_created_skip_unique.csv", "./analysis/cloc_hearted_skip_unique.csv", 'Arduino Sketch')
analyse_cloc("./analysis/cloc_created_skip_unique.csv", "./analysis/cloc_hearted_skip_unique.csv", 'HTML')


df_created1 = load_json("../cr_report_created_half1.json")  # 6010 -- len(df["reports"])
df_created2 = load_json("../cr_report_created_half2.json")  # 6112
df_hearted1 = load_json("../cr_report_hearted_half1.json")  # 3311
df_hearted2 = load_json("../cr_report_hearted_half2.json")  # 8341

# Stats
stats_created1 = get_cr_stats(df_created1)
stats_created2 = get_cr_stats(df_created2)

stats_hearted1 = get_cr_stats(df_hearted1)
stats_hearted2 = get_cr_stats(df_hearted2)

stats_created_joined = join_cr_stats(stats_created1, stats_created2)
stats_hearted_joined = join_cr_stats(stats_hearted1, stats_hearted2)
write_dict(stats_created_joined, "./analysis/cr/data_jsons/stats_created_joined.json")
write_dict(stats_hearted_joined, "./analysis/cr/data_jsons/stats_hearted_joined.json")

stats_total_joined = join_cr_stats(stats_created_joined, stats_hearted_joined)
write_dict(stats_total_joined, "./analysis/cr/data_jsons/stats_total_joined.json")

analyse_cr_stats(stats_created_joined, "created")
analyse_cr_stats(stats_hearted_joined, "hearted")
analyse_cr_stats(stats_total_joined, "total")


# LOC - Params
loc_param_created1 = get_cr_loc_param(df_created1)
loc_param_created2 = get_cr_loc_param(df_created2)

loc_param_hearted1 = get_cr_loc_param(df_hearted1)
loc_param_hearted2 = get_cr_loc_param(df_hearted2)

loc_param_created_joined = join_cr_loc_param(loc_param_created1, loc_param_created2)
loc_param_hearted_joined = join_cr_loc_param(loc_param_hearted1, loc_param_hearted2)
write_dict(loc_param_created_joined, "./analysis/cr/data_jsons/loc_param_created_joined.json")
write_dict(loc_param_hearted_joined, "./analysis/cr/data_jsons/loc_param_hearted_joined.json")

loc_param_total_joined = join_cr_loc_param(loc_param_created_joined, loc_param_hearted_joined)
write_dict(loc_param_total_joined, "./analysis/cr/data_jsons/loc_param_total_joined.json")

analyse_cr_loc_param(loc_param_created_joined, "created")
analyse_cr_loc_param(loc_param_hearted_joined, "hearted")
analyse_cr_loc_param(loc_param_total_joined, "total")


# Metrics
metrics_created1 = get_cr_metrics(df_created1)
metrics_created2 = get_cr_metrics(df_created2)

metrics_hearted1 = get_cr_metrics(df_hearted1)
metrics_hearted2 = get_cr_metrics(df_hearted2)

metrics_created_joined = join_cr_metrics(metrics_created1, metrics_created2)
metrics_hearted_joined = join_cr_metrics(metrics_hearted1, metrics_hearted2)
write_dict(metrics_created_joined, "./analysis/cr/data_jsons/metrics_created_joined.json")
write_dict(metrics_hearted_joined, "./analysis/cr/data_jsons/metrics_hearted_joined.json")

metrics_total_joined = join_cr_metrics(metrics_created_joined, metrics_hearted_joined)
write_dict(metrics_total_joined, "./analysis/cr/data_jsons/metrics_total_joined.json")

analyse_cr_metrics(metrics_created_joined, "created")
analyse_cr_metrics(metrics_hearted_joined, "hearted")
analyse_cr_metrics(metrics_total_joined, "total")
