from dash import html, dcc

def welcome_page():
    return html.Div([
        html.Div([
            html.Div([
                html.H1("Budgetr.", className='welcome-logo'),
                dcc.Link("Sign In", href='/sign_in', className='sign-in-btn'),
                dcc.Link("Create Your Account", href='/sign_up', className='sign-up-btn')    
            ], className= 'welcome-nav')
        ], className= 'welcome-nav-background'),
        html.Div([
            html.Div([
                html.Div([
                    html.H1("Visualize Your Finances", className='welcome-slogan'),
                    html.P("Gain control over your expenses. Discover clear, visual insights into your spending to help you budget smarter and save more.", className='welcome-paragraph'),
                    dcc.Link("Start Today", href='/sign_up', className='sign-up-btn')                          
                ], className='welcome-text'),
                html.Img(src= '/assets/wallet.png', className='welcome-image')
            ], className= "welcome-content")
        ], className='welcome-content-background'),

        html.Div([
            html.Div([
                html.H2("About The Creators"),
                html.P("After meeting in ECSE 428, a pivotal software engineering course at McGill University, Masa and Shyam quickly discovered their shared passion for technology and innovation. This connection sparked not only a dynamic classroom collaboration but also inspired them to tackle summer projects together, blending their skills to create impactful solutions."),
                html.P("We're also just bored."),
                html.Div([
                    html.Div([
                        html.Img(src='assets/masa.png', className='creator-image'),
                        html.H3('Nagamasa (Masa) Kagami'),
                        html.P('Electrical Engineering Student @ McGill University'),
                        html.Div([
                            dcc.Link('LinkedIn', href='https://www.linkedin.com/in/nagamasa', className='social-link'),
                            dcc.Link('Personal Website', href='https://www.masakagami.com', className='social-link')
                        ], className='links-container')
                    ], className='creator-profile'),
                    html.Div([
                        html.Img(src='/path_to_partner_image.jpg', className='creator-image'),
                        html.H3('Partner Name'),
                        html.P('Software Engineering Student @ McGill University'),
                        html.Div([
                            dcc.Link('LinkedIn', href='https://www.linkedin.com/in/', className='social-link'),
                            dcc.Link('Personal Website', href='masakagami.com', className='social-link')
                        ])
                    ], className='creator-profile')
                ], className='creators-container')
            ], className='welcome-about')  
        ], className='welcome-about-background')


    ],className='welcome')