The <u>_create_</u> function is used to generate a **CSV** file with predicted and real positions for use by the <u>_analysis_</u> function.

Note the change to the file location of lines seven through ten of the <u>_create_</u> function. The code is as follows.
>im2gps_predict = pd.read_csv('im2gps_rgb_images.csv')
>im2gps_truth = pd.read_csv('im2gps_places365.csv')
>im2gps3k_predict = pd.read_csv('im2gps3k_rgb_images.csv')
>im2gps3k_truth = pd.read_csv('im2gps3k_places365.csv')

**All** generated files are generated and saved in the **root directory**.

The environmental documentation is available at _requirementsa.txt_

Just run the <u>_run_</u> function directly

