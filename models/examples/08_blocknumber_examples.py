from datetime import datetime, timedelta, timezone

from credmark.cmf.model import Model
from credmark.cmf.model.errors import ModelInputError, ModelRunError
from credmark.cmf.types.block_number import (BlockNumber,
                                             BlockNumberOutOfRangeError)
from credmark.dto import DTO, DTOField, EmptyInput
from models.examples.example_dtos import ExampleModelOutput


@Model.describe(slug='example.block-number',
                version='1.0',
                display_name='BlockNumber Usage Examples',
                description='This model gives examples of \
                             the functionality available on the BlockNumber class',
                developer='Credmark',
                input=EmptyInput,
                output=ExampleModelOutput)
class ExampleBlockNumber(Model):

    def run(self, _) -> ExampleModelOutput:
        output = ExampleModelOutput(
            github_url="https://github.com/credmark/credmark-models-py/blob/main/models/examples/08_blocknumber_examples.py",
            documentation_url="https://developer-docs.credmark.com/en/latest/reference/credmark.cmf.types.block_number.BlockNumber.html")

        output.log("This model demonstrates the functionality of the BlockNumber class")

        block_number = self.context.block_number

        output.log("The current environment's BlockNumber is available in the Model Context")
        output.log_io(input="self.context.block_number",
                      output=self.context.block_number)
        output.log_io(input="block_number",
                      output=block_number)
        output.log_io(input="block_number.timestamp",
                      output=block_number.timestamp)
        output.log_io(input="block_number.timestamp_datetime",
                      output=block_number.timestamp_datetime)

        output.log('Addition and subtraction works across BlockNumber and int types')
        output.log_io(input="block_number - 1000",
                      output=block_number - 1000)
        output.log_io(input="(block_number - 1000).timestamp_datetime",
                      output=(block_number - 1000).timestamp_datetime)
        output.log_io(input="block_number.from_datetime(block_number.timestamp - 3600)",
                      output=block_number.from_timestamp(block_number.timestamp - 3600))
        output.log_io(input="BlockNumber.from_datetime(block_number.timestamp - 3600)",
                      output=BlockNumber.from_timestamp(block_number.timestamp - 3600))

        # NOTE: THE FOLLOWING IS FOR DEMONSTRATION ONLY.
        # You should NOT catch BlockNumberOutOfRangeError or
        # other ModelRunErrors in your models!

        try:
            block_number + 1
            raise ModelRunError(
                message='BlockNumbers cannot exceed the current context.block_number, '
                'an exception was NOT caught, and the example has FAILED')
        except BlockNumberOutOfRangeError as _e:
            output.log_error(_e)
            output.log_error("Attempting to create a BlockNumber object higher than the current "
                             "context's block_number raises BlockNumberOutOfRangeError")

        try:
            BlockNumber(-1)
            raise ModelRunError(
                message="BlockNumbers cannot be negative, an exception was NOT caught, "
                "and the example has FAILED")
        except BlockNumberOutOfRangeError as _e:
            output.log_error(_e)
            output.log_error(
                "Attempting to create a BlockNumber object with a negative block number "
                "raises BlockNumberOutOfRangeError")

        return output


class _BlockTimeInput(DTO):
    blockTime: datetime = DTOField(
        title="Block time",
        description="Unix time, i.e. seconds(if >= -2e10 or <= 2e10) or milliseconds "
        "(if < -2e10 or > 2e10) since 1 January 1970 or string with format "
        "YYYY-MM-DD[T]HH: MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]",
        default_factory=datetime.utcnow
    )


@Model.describe(slug='example.block-time',
                version='1.0',
                display_name='(Example) BlockNumber',
                description='The Time of the block of the execution context',
                input=_BlockTimeInput,
                output=ExampleModelOutput)
class BlockTimeExample(Model):
    def run(self, input: _BlockTimeInput) -> ExampleModelOutput:
        output = ExampleModelOutput(
            github_url="https://github.com/credmark/credmark-models-py/blob/main/models/examples/08_blocknumber_examples.py",
            documentation_url="https://developer-docs.credmark.com/en/latest/reference/credmark.cmf.types.block_number.BlockNumber.html")

        output.log("This model demonstrates the conversion between block_number, timestamp and Python datetime")

        block_time = input.blockTime.replace(tzinfo=timezone.utc)
        output.log_io(input="Input blockTime", output=block_time)

        output.log("CMF's BlockNumber is used to get Block Number from datetime or timestamp")
        block_number = BlockNumber.from_timestamp(block_time)
        output.log("BlockNumber's timestamp might be different from the input timestamp,")
        output.log("as the last block before the datetime is returned")
        output.log_io(input=f"BlockNumber.from_timestamp({block_time})", output=block_number)

        output.log_io(input="block_number.timestamp_datetime", output=block_number.timestamp_datetime)

        output.log("Block Number can also be obtained from unix timestamp.")
        output.log("If timezone is not provided, python defaults to UTC timezone")
        output.log(f"{block_time} = {block_time.timestamp()}s")
        output.log_io(input=f"BlockNumber.from_timestamp({block_time.timestamp()})",
                      output=BlockNumber.from_timestamp(block_time.timestamp()))

        output.log("Querying block number for a future timestamp returns the latest block number")
        future_block_time = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=10)
        output.log_io(input="future_block_time", output=future_block_time)
        output.log_io(input=f"BlockNumber.from_timestamp({future_block_time})",
                      output=BlockNumber.from_timestamp(future_block_time))

        block_time_without_tz = block_time.replace(tzinfo=None)
        output.log_io(input="block_time_without_tz", output=block_time_without_tz)

        try:
            BlockNumber.from_timestamp(block_time_without_tz)
            raise ModelRunError(
                message='BlockNumber cannot be converted from a datetime without timezone, '
                'an exception was NOT caught, and the example has FAILED')
        except ModelInputError as _e:
            output.log_error(_e)
            output.log_error("Attempting to convert a datetime without timezone to BlockNumber "
                             "raises ModelInputError")
        return output
