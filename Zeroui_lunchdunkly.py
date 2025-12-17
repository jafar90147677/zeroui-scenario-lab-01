import os
import ldclient
from ldclient import Context
from ldclient.config import Config

if __name__ == '__main__':
    # Set your LaunchDarkly SDK key.
    # This is inlined as example only for onboarding.
    # Never hardcode your SDK key in production.
    ldclient.set_config(Config('sdk-51798d2b-64c3-4157-87cf-bc7cf387763b'))

    if not ldclient.get().is_initialized():
        print('SDK failed to initialize')
        exit()

    # A "context" is a data object representing users, devices, organizations, and
    # other entities. You'll need this later, but you can ignore it for now.
    context = (
        Context.builder('EXAMPLE_CONTEXT_KEY')
        .kind('user')
        .set('email', 'biz@face.dev')
        .build()
    )

    # For onboarding purposes only we flush events as soon as
    # possible so we quickly detect your connection.
    # You don't have to do this in practice because events are automatically flushed.
    ldclient.get().flush()
    print('SDK successfully initialized')