# Install libraries
```bash
pip install shiny
pip install shinywidgets
pip install plotly pandas
pip install rsconnect-python
```

# Run app
```bash
shiny run --reload app.py
```

# Export the `requirements.txt`
```bash
pip install pipreqs
pipreqs code --force
```

# Push code to `shinyapps.io`
```bash
rsconnect add --account triphan-viz --name triphan-viz --token <TOKEN> --secret <SECRET>
rsconnect deploy shiny code --name triphan-viz --title hiv-dashboard
```