import asyncio
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Third-party imports
from browser_use import Agent, Controller

# Local imports
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext

# Load environment variables.
load_dotenv()

# Initialize language model and controller.
llm = ChatOpenAI(model='gpt-4o')
controller = Controller()


@pytest.mark.skip(reason='this is for local testing only')
async def test_wait_for_element():
	"""Test 'Wait for element' action."""

	initial_actions = [
		{'open_tab': {'url': 'https://pypi.org/'}},
		# Uncomment the line below to include the wait action in initial actions.
		# {'wait_for_element': {'selector': '#search', 'timeout': 30}},
	]

	# Set up the browser context.
	context = BrowserContext(
		browser=Browser(config=BrowserConfig(headless=False, disable_security=True)),
	)

	# Create the agent with the task.
	agent = Agent(
		task="Wait for element '#search' to be visible with a timeout of 30 seconds.",
		llm=llm,
		browser_context=context,
		initial_actions=initial_actions,
		controller=controller,
	)

	# Run the agent for a few steps to trigger navigation and then the wait action.
	history = await agent.run(max_steps=3)
	action_names = history.action_names()

	# Ensure that the wait_for_element action was executed.
	assert 'wait_for_element' in action_names, 'Expected wait_for_element action to be executed.'

	# Verify that the #search element is visible by querying the page.
	page = await context.get_current_page()
	header_handle = await page.query_selector('#search')
	assert header_handle is not None, 'Expected to find a #search element on the page.'
	is_visible = await header_handle.is_visible()
	assert is_visible, 'Expected the #search element to be visible.'


if __name__ == '__main__':
	asyncio.run(test_wait_for_element())
