"""
DREAM AI - Deals API Endpoint Implementation
Task 1.6: Backend API - Create Deal Endpoint
PRD Reference: Section 9.1
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator, field_validator
from decimal import Decimal
from datetime import datetime
from uuid import UUID
import logging

from prisma import Prisma
from prisma.models import Deal, Organization, User

# Initialize router
deals_router = APIRouter(prefix="/api/v1/deals", tags=["deals"])

# Logger
logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE SCHEMAS (Matching PRD Section 9.1)
# ============================================================================

class AddressSchema(BaseModel):
    """Address object from PRD"""
    street: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    zip: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')

class SourceSchema(BaseModel):
    """Source information object from PRD"""
    type: Optional[str] = Field(None, alias="type")  # source_type_enum
    name: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

class DealCreateRequest(BaseModel):
    """Request body matching PRD Section 9.1"""
    property_name: str = Field(..., min_length=3, max_length=100)
    address: Optional[AddressSchema] = None
    property_type: Optional[str] = "MULTIFAMILY"  # property_type_enum
    property_class: Optional[str] = None  # property_class_enum (A, B, C, D)
    year_built: Optional[int] = None
    units: Optional[int] = Field(None, gt=0, le=9999)
    asking_price: Optional[Decimal] = Field(None, gt=0)
    occupancy: Optional[Decimal] = Field(None, ge=0, le=1)  # 0-1 range (0-100%)
    noi_in_place: Optional[Decimal] = Field(None, ge=0)
    noi_pro_forma: Optional[Decimal] = Field(None, ge=0)
    source: Optional[SourceSchema] = None
    notes: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = Field(None, max_items=20)
    priority: Optional[str] = "MEDIUM"  # priority_enum
    how_received: Optional[str] = "EMAIL"  # how_received_enum
    market_status: Optional[str] = "LISTED"  # market_status_enum

    @field_validator('year_built')
    @classmethod
    def validate_year_built(cls, v):
        """Validate year built: 1800 <= year <= current year"""
        if v is not None:
            current_year = datetime.now().year
            if v < 1800 or v > current_year:
                raise ValueError(f"Year built must be between 1800 and {current_year}")
        return v

    @field_validator('property_type')
    @classmethod
    def validate_property_type(cls, v):
        """Validate property type enum"""
        valid_types = [
            'MULTIFAMILY', 'SINGLE_FAMILY', 'STUDENT_HOUSING',
            'SENIOR_HOUSING', 'MOBILE_HOME_PARK', 'MIXED_USE', 'OTHER'
        ]
        if v and v not in valid_types:
            raise ValueError(f"Property type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator('property_class')
    @classmethod
    def validate_property_class(cls, v):
        """Validate property class enum"""
        if v and v not in ['A', 'B', 'C', 'D']:
            raise ValueError("Property class must be A, B, C, or D")
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        """Validate priority enum"""
        if v and v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError("Priority must be LOW, MEDIUM, or HIGH")
        return v

    @field_validator('how_received')
    @classmethod
    def validate_how_received(cls, v):
        """Validate how_received enum"""
        valid = ['EMAIL', 'PHONE', 'IN_PERSON', 'WEBSITE', 'REFERRAL', 'OTHER']
        if v and v not in valid:
            raise ValueError(f"How received must be one of: {', '.join(valid)}")
        return v

    @field_validator('market_status')
    @classmethod
    def validate_market_status(cls, v):
        """Validate market_status enum"""
        valid = ['LISTED', 'OFF_MARKET', 'PRE_MARKET', 'POCKET_LISTING', 'REO']
        if v and v not in valid:
            raise ValueError(f"Market status must be one of: {', '.join(valid)}")
        return v

    @field_validator('source')
    @classmethod
    def validate_source_type(cls, v):
        """Validate source type if provided"""
        if v and hasattr(v, 'type') and v.type:
            valid = [
                'BROKER', 'DIRECT_OWNER', 'AUCTION', 'WHOLESALER',
                'NETWORK', 'LOOPNET_COSTAR', 'OTHER'
            ]
            if v.type not in valid:
                raise ValueError(f"Source type must be one of: {', '.join(valid)}")
        return v

    class Config:
        populate_by_name = True

class DealResponse(BaseModel):
    """Response matching PRD Section 9.1"""
    id: str
    created_at: datetime
    status: str  # deal_stage_enum (default: "NEW")
    property_name: str
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    property_type: Optional[str] = None
    units: Optional[int] = None
    asking_price: Optional[Decimal] = None
    occupancy: Optional[Decimal] = None
    noi_in_place: Optional[Decimal] = None
    priority: Optional[str] = None

    class Config:
        from_attributes = True

# ============================================================================
# VALIDATION FUNCTIONS (PRD Section 7.1)
# ============================================================================

def validate_deal_data(data: DealCreateRequest) -> List[str]:
    """
    Cross-field validation rules from PRD Section 7.1 and 7.2
    Returns list of validation error messages
    """
    errors = []

    # Field-level validations (Section 7.1)
    if data.units is not None and data.units <= 0:
        errors.append("Number of units is required (must be > 0)")

    if data.occupancy is not None and (data.occupancy < 0 or data.occupancy > 1):
        errors.append("Occupancy must be 0-100%")

    if data.asking_price is not None and data.asking_price <= 0:
        errors.append("Invalid asking price")

    # Cross-field validations (Section 7.2)
    if data.noi_in_place is not None and data.asking_price is not None:
        if data.noi_in_place >= data.asking_price:
            errors.append("NOI exceeds asking price - please verify")

    # Cap rate reasonableness check (Section 7.3)
    if data.asking_price and data.noi_in_place and data.asking_price > 0:
        cap_rate = float(data.noi_in_place / data.asking_price)
        if cap_rate < 0.03 or cap_rate > 0.12:
            errors.append(f"Cap rate ({cap_rate:.2%}) seems unusual, please verify")

    # Price per unit reasonableness check (Section 7.3)
    if data.asking_price and data.units and data.units > 0:
        ppu = float(data.asking_price / data.units)
        if ppu < 30000 or ppu > 500000:
            errors.append(f"Price per unit (${ppu:,.0f}) is outside typical range ($50K-$500K)")

    return errors

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_or_create_organization(prisma: Prisma, org_id: Optional[str] = None) -> Organization:
    """
    Get organization by ID or create default for testing.
    TODO: Replace with proper auth when authentication is implemented
    """
    if org_id:
        org = await prisma.organization.find_unique(where={"id": org_id})
        if org:
            return org
    
    # For now, create or get a default organization
    # TODO: Remove this when auth is implemented
    org = await prisma.organization.find_first()
    if not org:
        org = await prisma.organization.create(
            data={
                "name": "Default Organization",
                "subscriptionTier": "FREE"
            }
        )
    return org

async def get_or_create_user(prisma: Prisma, org_id: str, user_id: Optional[str] = None) -> User:
    """
    Get user by ID or create default for testing.
    TODO: Replace with proper auth when authentication is implemented
    """
    if user_id:
        user = await prisma.user.find_unique(where={"id": user_id})
        if user:
            return user
    
    # For now, create or get a default user
    # TODO: Remove this when auth is implemented
    user = await prisma.user.find_first(where={"organizationId": org_id})
    if not user:
        user = await prisma.user.create(
            data={
                "organizationId": org_id,
                "email": "default@dream.ai",
                "name": "Default User",
                "role": "ANALYST"
            }
        )
    return user

# ============================================================================
# API ENDPOINTS
# ============================================================================

@deals_router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreateRequest,
    # TODO: Add auth dependency when implemented
    # current_user: User = Depends(get_current_user),
    # organization_id: str = Depends(get_organization_id),
):
    """
    Create a new deal (Manual Entry).
    
    PRD Reference: Section 9.1
    Validation: Section 7.1, 7.2, 7.3
    
    Request Body Schema:
    - property_name (required): 3-100 characters
    - address: {street, city, state, zip}
    - property_type: MULTIFAMILY, SINGLE_FAMILY, etc.
    - units: > 0, <= 9999
    - asking_price: > 0
    - occupancy: 0-1 (0-100%)
    - noi_in_place: >= 0
    - source: {type, name, company, email, phone}
    - notes: max 2000 characters
    - tags: array of strings
    - priority: LOW, MEDIUM, HIGH
    
    Returns 201 Created with deal data.
    """
    prisma = Prisma()
    
    try:
        await prisma.connect()
        
        # Get organization and user (TODO: Replace with auth)
        organization = await get_or_create_organization(prisma)
        user = await get_or_create_user(prisma, organization.id)
        
        # Validate deal data (PRD Section 7.1, 7.2)
        validation_errors = validate_deal_data(deal_data)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Validation failed",
                    "errors": validation_errors
                }
            )
        
        # Prepare deal data for database
        deal_dict = {
            "organizationId": organization.id,
            "createdById": user.id,
            "propertyName": deal_data.property_name,
            "propertyType": deal_data.property_type,
            "stage": "NEW",  # Default stage
            "priority": deal_data.priority,
            "howReceived": deal_data.how_received,
            "marketStatus": deal_data.market_status,
        }
        
        # Address fields
        if deal_data.address:
            deal_dict["addressStreet"] = deal_data.address.street
            deal_dict["addressCity"] = deal_data.address.city
            deal_dict["addressState"] = deal_data.address.state
            deal_dict["addressZip"] = deal_data.address.zip
        
        # Property characteristics
        if deal_data.property_class:
            deal_dict["propertyClass"] = deal_data.property_class
        if deal_data.year_built:
            deal_dict["yearBuilt"] = deal_data.year_built
        if deal_data.units:
            deal_dict["units"] = deal_data.units
        
        # Financial fields
        if deal_data.asking_price:
            deal_dict["askingPrice"] = deal_data.asking_price
        if deal_data.occupancy:
            deal_dict["occupancy"] = deal_data.occupancy
        if deal_data.noi_in_place:
            deal_dict["noiInPlace"] = deal_data.noi_in_place
        if deal_data.noi_pro_forma:
            deal_dict["noiProForma"] = deal_data.noi_pro_forma
        
        # Source information
        if deal_data.source:
            deal_dict["sourceType"] = deal_data.source.type or "BROKER"
            deal_dict["sourceName"] = deal_data.source.name
            deal_dict["sourceCompany"] = deal_data.source.company
            deal_dict["sourceEmail"] = deal_data.source.email
            deal_dict["sourcePhone"] = deal_data.source.phone
        
        # Notes and tags
        if deal_data.notes:
            deal_dict["notes"] = deal_data.notes[:5000]  # Enforce max length
        
        # Create deal in database
        deal = await prisma.deal.create(data=deal_dict)
        
        # Handle tags (if provided)
        if deal_data.tags:
            # TODO: Create tags and link via DealTag junction table
            # For now, we'll skip tag creation to keep it simple
            # This can be implemented later
            pass
        
        logger.info(f"Deal created: {deal.id} - {deal.propertyName}")
        
        # Return response matching PRD format
        return DealResponse(
            id=deal.id,
            created_at=deal.createdAt,
            status=deal.stage,
            property_name=deal.propertyName,
            address_street=deal.addressStreet,
            address_city=deal.addressCity,
            address_state=deal.addressState,
            address_zip=deal.addressZip,
            property_type=deal.propertyType,
            units=deal.units,
            asking_price=deal.askingPrice,
            occupancy=deal.occupancy,
            noi_in_place=deal.noiInPlace,
            priority=deal.priority,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating deal: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deal: {str(e)}"
        )
    finally:
        await prisma.disconnect()

# ============================================================================
# GET DEALS ENDPOINT (Task 1.5: Deal List View)
# ============================================================================

class DealListItemResponse(BaseModel):
    """Deal list item response"""
    id: str
    property_name: str
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    property_type: Optional[str] = None
    property_class: Optional[str] = None
    units: Optional[int] = None
    asking_price: Optional[Decimal] = None
    occupancy: Optional[Decimal] = None
    stage: str
    priority: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DealListResponse(BaseModel):
    """Deal list response with pagination"""
    deals: List[DealListItemResponse]
    total: int
    page: int
    page_size: int

@deals_router.get("/", response_model=DealListResponse)
async def list_deals(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    property_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    # TODO: Add auth dependency when implemented
    # current_user: User = Depends(get_current_user),
):
    """
    List all deals with filtering, sorting, and pagination.
    
    PRD Reference: Section 9.1
    
    Query Parameters:
    - status: Filter by deal stage (NEW, SCREENING, LOI, etc.)
    - priority: Filter by priority (LOW, MEDIUM, HIGH)
    - property_type: Filter by property type (MULTIFAMILY, etc.)
    - page: Page number (1-indexed)
    - page_size: Number of deals per page
    - sort_by: Field to sort by (created_at, asking_price, property_name)
    - sort_order: Sort order (asc, desc)
    
    Returns paginated list of deals.
    """
    prisma = Prisma()
    
    try:
        await prisma.connect()
        
        # Get organization (TODO: Replace with auth)
        organization = await get_or_create_organization(prisma)
        
        # Build query filters
        where_clause = {
            "organizationId": organization.id,
            "deletedAt": None,  # Only non-deleted deals
        }
        
        if status:
            where_clause["stage"] = status
        if priority:
            where_clause["priority"] = priority
        if property_type:
            where_clause["propertyType"] = property_type
        
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Get total count
        total = await prisma.deal.count(where=where_clause)
        
        # Build order by
        order_by = {}
        if sort_by == "created_at":
            order_by["createdAt"] = sort_order
        elif sort_by == "asking_price":
            order_by["askingPrice"] = sort_order
        elif sort_by == "property_name":
            order_by["propertyName"] = sort_order
        else:
            order_by["createdAt"] = "desc"  # Default
        
        # Fetch deals
        deals = await prisma.deal.find_many(
            where=where_clause,
            skip=skip,
            take=page_size,
            order=order_by
        )
        
        # Convert to response format
        deal_items = [
            DealListItemResponse(
                id=deal.id,
                property_name=deal.propertyName,
                address_street=deal.addressStreet,
                address_city=deal.addressCity,
                address_state=deal.addressState,
                address_zip=deal.addressZip,
                property_type=deal.propertyType,
                property_class=deal.propertyClass,
                units=deal.units,
                asking_price=deal.askingPrice,
                occupancy=deal.occupancy,
                stage=deal.stage,
                priority=deal.priority,
                created_at=deal.createdAt,
            )
            for deal in deals
        ]
        
        return DealListResponse(
            deals=deal_items,
            total=total,
            page=page,
            page_size=page_size,
        )
        
    except Exception as e:
        logger.error(f"Error listing deals: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deals: {str(e)}"
        )
    finally:
        await prisma.disconnect()

