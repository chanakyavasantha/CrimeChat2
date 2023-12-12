from h2o_wave import main, app, Q, ui, on, handle_on
from h2o_wave import main, app, Q, ui, data
from h2o_wave import main, app, Q, ui,data
import asyncio
import pandas as pd




html = '''
<style>
.anim {
  font-weight: 900;
  font-size: 3.5em;
  color: #fec925;
}
.anim .letter {
  display: inline-block;
  line-height: 1em;
}
</style>

<h1 id="animation" class="anim">Welcome to H2o.ai's Wave Chat!</h1>
'''
script = '''
// Wrap every letter in a span
var textWrapper = document.querySelector('.anim');
textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>");

anime.timeline({loop: true})
  .add({
    targets: '.anim .letter',
    scale: [4,1],
    opacity: [0,1],
    translateZ: 0,
    easing: "easeOutExpo",
    duration: 950,
    delay: (el, i) => 70*i
  }).add({
    targets: '.anim',
    opacity: 0,
    duration: 1000,
    easing: "easeOutExpo",
    delay: 3000
  });
'''

'''
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
'''



async def stream_message(q: Q):
    stream = ''
    q.page['input'].data += [stream, False]
    # Show the "Stop generating" button
    q.page['input'].generating = True
    stream += 'This is a sample UI'
    q.page['input'].data[-1] = [stream, False]
    q.page['input'].generating = False
    
    
    await q.page.save()




@app('/CrimeApp')
async def serve(q: Q):

    q.client.dark_mode = True
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True
    if q.events.chatbot and q.events.chatbot.stop:
        # Cancel the streaming task.
        q.client.task.cancel()
        # Hide the "Stop generating" button.
        q.page['input'].generating = False
    # A new message arrived.
    elif q.args.chatbot:
        # Append user message.
        q.page['input'].data += [q.args.chatbot, True]
        # Run the streaming within cancelable asyncio task.
        q.client.task = asyncio.create_task(stream_message(q))
    # Other browser interactions
    await handle_on(q)
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()

    q.page['meta'] = ui.meta_card(
        box='',
        title='Wave Chat',
        theme='light',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
                max_width='1800px',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                        ui.zone('vertical', size='1', ),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )
    q.page['banner'] = ui.meta_card(
        box='',
        # Load anime.js
        scripts=[ui.script(path='https://cdnjs.cloudflare.com/ajax/libs/animejs/2.0.2/anime.min.js')],
        script=ui.inline_script(
            # The Javascript code for this script.
            content=script,
            # Execute this script only if the 'anime' library is available.
            requires=['anime'],
            # Execute this script only if the 'animation' element is available.
            targets=['animation'],
    ))
    q.page['header'] = ui.header_card(
        box='header',
        title='Wave Chat',
        subtitle="Welcome to H2o's Criminal Checker!",
        image='https://wave.h2o.ai/img/h2o-logo.svg',
        items=[ui.menu(icon='', items=[ui.command(name='change_theme', icon='ClearNight', label='Dark Mode')])]
    )
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made with 💛 using [H2O Wave](https://wave.h2o.ai).'
    )

    await home(q)


@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'banner_1',  ui.markup_card(box='horizontal',title=' ',content=html))
    add_card(q, 'input',ui.chatbot_card(box=f'vertical', data=data(fields='content from_user', t='list'),name='chatbot',events=['stop']))

@on()
async def change_theme(q: Q):
    """Change the app from light to dark mode"""
    if q.client.dark_mode:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='ClearNight', label='Dark mode')])]
        q.page["meta"].theme = "light"
        q.client.dark_mode = False
    else:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='Sunny', label='Light mode')])]
        q.page["meta"].theme = "h2o-dark"
        q.client.dark_mode = True


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
