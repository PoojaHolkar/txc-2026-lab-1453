#!/bin/bash

echo
echo "Here are the contents of the post_deploy_variables.json file:"
echo
cat ./post_deploy_variables.json
echo
echo "Here are the contents of the post_deploy_variables.yaml file:"
echo
cat ./post_deploy_variables.yaml
echo

cat > ./post_deploy_text_output.txt <<EOF
This is some sample text output for testing the use of
the post_deploy_text_output.txt file for passing back
output to the end user.
EOF

cat > ./post_deploy_json_output.json <<EOF
{"output_var1":"output_var1_value","output_var2":"output_var2_value"}
EOF

exit 0