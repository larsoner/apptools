class SelectionProviderNotFoundError(Exception):
    """ Raised when a provider is requested by ID and not found. """

    def __init__(self, provider_id):
        self.provider_id = provider_id

    def __str__(self):
        msg = "Selection provider with ID '{id}' not found."
        return msg.format(id=self.provider_id)


class IDConflictError(Exception):
    """ Raised when a provider is added and its ID is already registered. """

    def __init__(self, provider_id):
        self.provider_id = provider_id

    def __str__(self):
        msg = "A selection provider with ID '{id}' is already registered."
        return msg.format(id=self.provider_id)
