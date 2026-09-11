from datetime import date

from pydantic import BaseModel, Field, field_validator


# ==================================================
# CREATE COMPLAINT
# ==================================================

class ComplaintCreate(BaseModel):

    complaint_source: str = Field(min_length=1)

    customer_name: str = Field(min_length=1)

    product_name: str = Field(min_length=1)

    product_strength: str = Field(min_length=1)

    batch_number: str = Field(min_length=1)

    manufacturing_date: date | None = None

    expiry_date: date | None = None

    quantity_affected: str = Field(min_length=1)

    complaint_type: str = Field(min_length=1)

    complaint_date: date

    detailed_description: str = Field(min_length=1)

    initial_severity: str = Field(min_length=1)

    priority: str = Field(min_length=1)


    # ----------------------------------------------
    # MANUFACTURING DATE VALIDATION
    # ----------------------------------------------

    @field_validator("manufacturing_date")
    @classmethod
    def validate_manufacturing_date(cls, value):

        if value is None:
            return value

        return value


    # ----------------------------------------------
    # EXPIRY DATE VALIDATION
    # ----------------------------------------------

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, value):

        if value is None:
            return value

        return value


    # ----------------------------------------------
    # DATE RELATIONSHIP VALIDATION
    # ----------------------------------------------

    @field_validator("expiry_date")
    @classmethod
    def validate_dates(cls, value, info):

        manufacturing_date = info.data.get(
            "manufacturing_date"
        )

        if (
            value is not None
            and manufacturing_date is not None
            and value < manufacturing_date
        ):
            raise ValueError(
                "Expiry date cannot be before manufacturing date."
            )

        return value


# ==================================================
# PARSE COMPLAINT REQUEST
# ==================================================

class ComplaintParseRequest(BaseModel):

    text: str = Field(min_length=1)


# ==================================================
# PARSE COMPLAINT RESPONSE
# ==================================================

class ComplaintParseResponse(BaseModel):

    complaint_source: str | None = None

    customer_name: str | None = None

    product_name: str | None = None

    product_strength: str | None = None

    batch_number: str | None = None

    manufacturing_date: date | None = None

    expiry_date: date | None = None

    quantity_affected: str | None = None

    originating_site: str | None = None

    block_impacted: str | None = None

    npm: str | None = None

    complaint_type: str | None = None

    detailed_description: str | None = None

    initial_severity: str | None = None

    suggested_next_action: str | None = None

    initial_risk_assessment: str | None = None

    priority: str | None = None