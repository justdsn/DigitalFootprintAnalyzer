# =============================================================================
# TESTS FOR LIGHT SCAN SERVICE
# =============================================================================
# Tests for the Google Dorking-based profile discovery functionality.
# =============================================================================

"""
Test Suite for Light Scan Service

Tests cover:
- LightScanService: Query generation for name, email, username
- URL validation for each platform
- Result deduplication
- Response schema validation
"""

import pytest
import asyncio
from app.services.scan.light_scan import LightScanService


# =============================================================================
# LIGHT SCAN SERVICE TESTS
# =============================================================================

class TestLightScanService:
    """Tests for LightScanService class."""
    
    @pytest.fixture
    def service(self):
        """Create a LightScanService instance."""
        return LightScanService()
    
    # -------------------------------------------------------------------------
    # QUERY GENERATION FOR NAME TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_name_queries(self, service):
        """Test query generation for name identifier."""
        queries = service._generate_queries("name", "John Perera", "Sri Lanka")
        
        # Should have queries for all platforms
        assert len(queries) == 4
        assert "facebook" in queries
        assert "instagram" in queries
        assert "linkedin" in queries
        assert "x" in queries
        
    def test_generate_name_queries_with_location(self, service):
        """Test that name queries include location filter."""
        queries = service._generate_queries("name", "John Perera", "Colombo")
        
        for platform_id, platform_queries in queries.items():
            # Should have at least one query with location
            location_queries = [q for q in platform_queries if "Colombo" in q]
            assert len(location_queries) >= 1
    
    def test_generate_name_queries_default_location(self, service):
        """Test that default location is Sri Lanka."""
        queries = service._generate_queries("name", "John Perera", "Sri Lanka")
        
        for platform_id, platform_queries in queries.items():
            # Should have query with Sri Lanka
            sri_lanka_queries = [q for q in platform_queries if "Sri Lanka" in q]
            assert len(sri_lanka_queries) >= 1
    
    def test_generate_name_queries_without_location(self, service):
        """Test query generation without location filter."""
        queries = service._generate_queries("name", "John Perera", None)
        
        for platform_id, platform_queries in queries.items():
            # At least one query should exist (basic name search)
            assert len(platform_queries) >= 1
    
    # -------------------------------------------------------------------------
    # QUERY GENERATION FOR EMAIL TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_email_queries(self, service):
        """Test query generation for email identifier."""
        queries = service._generate_queries("email", "john.perera@gmail.com", "Sri Lanka")
        
        # Should have queries for all platforms
        assert len(queries) == 4
        
        for platform_id, platform_queries in queries.items():
            # Should have queries for full email and username portion
            assert len(platform_queries) >= 2
    
    def test_generate_email_queries_extracts_username(self, service):
        """Test that email queries extract and search username portion."""
        queries = service._generate_queries("email", "john.perera@gmail.com", "Sri Lanka")
        
        for platform_id, platform_queries in queries.items():
            # Should have query with extracted username
            username_queries = [q for q in platform_queries if "john.perera" in q.lower()]
            assert len(username_queries) >= 1
    
    def test_generate_email_queries_searches_full_email(self, service):
        """Test that email queries search for full email."""
        queries = service._generate_queries("email", "john@example.com", "Sri Lanka")
        
        for platform_id, platform_queries in queries.items():
            # Should have query with full email
            full_email_queries = [q for q in platform_queries if "john@example.com" in q]
            assert len(full_email_queries) >= 1
    
    def test_generate_email_queries_removes_special_chars(self, service):
        """Test that email username variations remove special characters."""
        queries = service._generate_queries("email", "john.perera@gmail.com", "Sri Lanka")
        
        # Should have variation without dots
        all_queries = []
        for platform_queries in queries.values():
            all_queries.extend(platform_queries)
        
        # Check that johnperera (without dot) is searched
        clean_username_queries = [q for q in all_queries if "johnperera" in q.lower()]
        assert len(clean_username_queries) >= 1
    
    # -------------------------------------------------------------------------
    # QUERY GENERATION FOR USERNAME TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_username_queries(self, service):
        """Test query generation for username identifier."""
        queries = service._generate_queries("username", "john_doe", "Sri Lanka")
        
        # Should have queries for all platforms
        assert len(queries) == 4
        
        for platform_id, platform_queries in queries.items():
            # Should have multiple queries for variations
            assert len(platform_queries) >= 2
    
    def test_generate_username_queries_strips_at_symbol(self, service):
        """Test that @ symbol is stripped from usernames."""
        queries = service._generate_queries("username", "@john_doe", "Sri Lanka")
        
        for platform_id, platform_queries in queries.items():
            # No query should contain @john_doe
            at_queries = [q for q in platform_queries if "@john_doe" in q]
            assert len(at_queries) == 0
            
            # Should contain john_doe
            clean_queries = [q for q in platform_queries if "john_doe" in q.lower()]
            assert len(clean_queries) >= 1
    
    def test_generate_username_variations(self, service):
        """Test username variation generation."""
        variations = service._generate_username_variations("john_doe")
        
        assert "john_doe" in variations
        assert "johndoe" in variations  # Without underscore
        assert "john.doe" in variations  # With dot instead
    
    def test_generate_username_variations_with_dots(self, service):
        """Test username variation generation with dots."""
        variations = service._generate_username_variations("john.doe")
        
        assert "john.doe" in variations
        assert "johndoe" in variations  # Without dot
        assert "john_doe" in variations  # With underscore instead
    
    # -------------------------------------------------------------------------
    # PLATFORM CONFIGURATION TESTS
    # -------------------------------------------------------------------------
    
    def test_platforms_configuration(self, service):
        """Test that all platforms are configured correctly."""
        assert "facebook" in service.PLATFORMS
        assert "instagram" in service.PLATFORMS
        assert "linkedin" in service.PLATFORMS
        assert "x" in service.PLATFORMS
    
    def test_platform_has_emoji(self, service):
        """Test that each platform has an emoji configured."""
        for platform_id, config in service.PLATFORMS.items():
            assert "emoji" in config
            assert len(config["emoji"]) > 0
    
    def test_platform_has_dork_base(self, service):
        """Test that each platform has a dork base configured."""
        for platform_id, config in service.PLATFORMS.items():
            assert "dork_base" in config
            assert "site:" in config["dork_base"]
    
    def test_facebook_dork_base(self, service):
        """Test Facebook dork base configuration."""
        assert service.PLATFORMS["facebook"]["dork_base"] == "site:facebook.com"
    
    def test_instagram_dork_base(self, service):
        """Test Instagram dork base configuration."""
        assert service.PLATFORMS["instagram"]["dork_base"] == "site:instagram.com"
    
    def test_linkedin_dork_base(self, service):
        """Test LinkedIn dork base configuration."""
        assert service.PLATFORMS["linkedin"]["dork_base"] == "site:linkedin.com/in"
    
    def test_x_dork_base(self, service):
        """Test X/Twitter dork base configuration."""
        dork_base = service.PLATFORMS["x"]["dork_base"]
        assert "site:x.com" in dork_base
        assert "site:twitter.com" in dork_base
    
    # -------------------------------------------------------------------------
    # URL VALIDATION TESTS
    # -------------------------------------------------------------------------
    
    def test_valid_facebook_profile_url(self, service):
        """Test that valid Facebook profile URLs are accepted."""
        assert service._is_valid_profile_url(
            "https://www.facebook.com/john.doe", "facebook"
        )
        assert service._is_valid_profile_url(
            "https://facebook.com/johndoe123", "facebook"
        )
    
    def test_valid_instagram_profile_url(self, service):
        """Test that valid Instagram profile URLs are accepted."""
        assert service._is_valid_profile_url(
            "https://www.instagram.com/john_doe/", "instagram"
        )
        assert service._is_valid_profile_url(
            "https://instagram.com/johndoe", "instagram"
        )
    
    def test_valid_linkedin_profile_url(self, service):
        """Test that valid LinkedIn profile URLs are accepted."""
        assert service._is_valid_profile_url(
            "https://www.linkedin.com/in/john-doe", "linkedin"
        )
        assert service._is_valid_profile_url(
            "https://linkedin.com/in/johndoe/", "linkedin"
        )
    
    def test_valid_x_profile_url(self, service):
        """Test that valid X/Twitter profile URLs are accepted."""
        assert service._is_valid_profile_url(
            "https://x.com/johndoe", "x"
        )
        assert service._is_valid_profile_url(
            "https://twitter.com/john_doe", "x"
        )
    
    def test_invalid_search_page_url(self, service):
        """Test that search page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://facebook.com/search?q=john", "facebook"
        )
        assert not service._is_valid_profile_url(
            "https://instagram.com/explore", "instagram"
        )
    
    def test_invalid_help_page_url(self, service):
        """Test that help page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://facebook.com/help", "facebook"
        )
        assert not service._is_valid_profile_url(
            "https://instagram.com/about", "instagram"
        )
    
    def test_invalid_login_page_url(self, service):
        """Test that login/signup page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://facebook.com/login", "facebook"
        )
        assert not service._is_valid_profile_url(
            "https://instagram.com/signup", "instagram"
        )
    
    def test_invalid_groups_page_url(self, service):
        """Test that Facebook groups page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://facebook.com/groups/somegroup", "facebook"
        )
    
    def test_invalid_events_page_url(self, service):
        """Test that Facebook events page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://facebook.com/events/12345", "facebook"
        )
    
    def test_invalid_reel_page_url(self, service):
        """Test that Instagram reel page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://instagram.com/reel/abc123", "instagram"
        )
    
    def test_invalid_hashtag_page_url(self, service):
        """Test that X hashtag page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://x.com/hashtag/tech", "x"
        )
    
    def test_invalid_linkedin_jobs_url(self, service):
        """Test that LinkedIn jobs page URLs are rejected."""
        assert not service._is_valid_profile_url(
            "https://linkedin.com/jobs/view/12345", "linkedin"
        )
    
    # -------------------------------------------------------------------------
    # SCAN RESPONSE TESTS
    # -------------------------------------------------------------------------
    
    @pytest.mark.asyncio
    async def test_scan_returns_correct_structure(self, service):
        """Test that scan returns correct response structure."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        # Check required fields
        assert "success" in result
        assert "scan_type" in result
        assert "scan_id" in result
        assert "identifier" in result
        assert "location" in result
        assert "scan_duration_seconds" in result
        assert "total_results" in result
        assert "platforms" in result
        assert "summary" in result
        assert "all_urls" in result
        assert "deep_scan_available" in result
        assert "deep_scan_message" in result
    
    @pytest.mark.asyncio
    async def test_scan_type_is_light(self, service):
        """Test that scan_type is 'light'."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        assert result["scan_type"] == "light"
    
    @pytest.mark.asyncio
    async def test_scan_id_format(self, service):
        """Test that scan_id has correct format (LS-XXXXXXXX)."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        assert result["scan_id"].startswith("LS-")
        assert len(result["scan_id"]) == 11  # LS- + 8 chars
    
    @pytest.mark.asyncio
    async def test_scan_identifier_in_response(self, service):
        """Test that identifier is correctly returned in response."""
        result = await service.scan(
            identifier_type="name",
            identifier_value="John Perera"
        )
        
        assert result["identifier"]["type"] == "name"
        assert result["identifier"]["value"] == "John Perera"
    
    @pytest.mark.asyncio
    async def test_scan_default_location(self, service):
        """Test that default location is Sri Lanka."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        assert result["location"] == "Sri Lanka"
    
    @pytest.mark.asyncio
    async def test_scan_custom_location(self, service):
        """Test that custom location is used."""
        result = await service.scan(
            identifier_type="name",
            identifier_value="John Perera",
            location="Colombo"
        )
        
        assert result["location"] == "Colombo"
    
    @pytest.mark.asyncio
    async def test_scan_platforms_in_response(self, service):
        """Test that all platforms are included in response."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        platform_ids = [p["platform"] for p in result["platforms"]]
        assert "facebook" in platform_ids
        assert "instagram" in platform_ids
        assert "linkedin" in platform_ids
        assert "x" in platform_ids
    
    @pytest.mark.asyncio
    async def test_scan_summary_structure(self, service):
        """Test that summary contains all platforms."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        summary = result["summary"]
        assert "facebook" in summary
        assert "instagram" in summary
        assert "linkedin" in summary
        assert "x" in summary
    
    # -------------------------------------------------------------------------
    # ERROR HANDLING TESTS
    # -------------------------------------------------------------------------
    
    @pytest.mark.asyncio
    async def test_scan_rejects_phone_type(self, service):
        """Test that phone identifier type is rejected."""
        with pytest.raises(ValueError) as excinfo:
            await service.scan(
                identifier_type="phone",
                identifier_value="0771234567"
            )
        
        assert "phone" in str(excinfo.value).lower() or "invalid" in str(excinfo.value).lower()
    
    @pytest.mark.asyncio
    async def test_scan_rejects_empty_identifier(self, service):
        """Test that empty identifier value is rejected."""
        with pytest.raises(ValueError):
            await service.scan(
                identifier_type="username",
                identifier_value=""
            )
        
        with pytest.raises(ValueError):
            await service.scan(
                identifier_type="username",
                identifier_value="   "
            )
    
    @pytest.mark.asyncio
    async def test_scan_rejects_invalid_type(self, service):
        """Test that invalid identifier type is rejected."""
        with pytest.raises(ValueError):
            await service.scan(
                identifier_type="invalid_type",
                identifier_value="test"
            )
    
    # -------------------------------------------------------------------------
    # UTILITY METHOD TESTS
    # -------------------------------------------------------------------------
    
    def test_get_supported_platforms(self, service):
        """Test get_supported_platforms returns all platforms."""
        platforms = service.get_supported_platforms()
        
        assert "facebook" in platforms
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "x" in platforms
    
    def test_get_platform_config(self, service):
        """Test get_platform_config returns correct config."""
        config = service.get_platform_config("facebook")
        
        assert config is not None
        assert "emoji" in config
        assert "dork_base" in config
        assert "exclude_paths" in config
    
    def test_get_platform_config_invalid(self, service):
        """Test get_platform_config returns None for invalid platform."""
        config = service.get_platform_config("invalid_platform")
        
        assert config is None


# =============================================================================
# RESULT DEDUPLICATION TESTS
# =============================================================================

class TestResultDeduplication:
    """Tests for result deduplication functionality."""
    
    @pytest.fixture
    def service(self):
        """Create a LightScanService instance."""
        return LightScanService()
    
    @pytest.mark.asyncio
    async def test_deduplication_in_scan_results(self, service):
        """Test that duplicate URLs are deduplicated in scan results."""
        # Since we can't easily control the external search results,
        # we test that the result structure supports deduplication
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        # Check that each platform's results have unique URLs
        for platform_data in result["platforms"]:
            urls = [r["url"] for r in platform_data["results"]]
            assert len(urls) == len(set(urls)), "Duplicate URLs found in results"


# =============================================================================
# PLATFORM EMOJI TESTS
# =============================================================================

class TestPlatformEmojis:
    """Tests for platform emoji configuration."""
    
    @pytest.fixture
    def service(self):
        """Create a LightScanService instance."""
        return LightScanService()
    
    def test_facebook_emoji(self, service):
        """Test Facebook emoji."""
        assert service.PLATFORMS["facebook"]["emoji"] == "📘"
    
    def test_instagram_emoji(self, service):
        """Test Instagram emoji."""
        assert service.PLATFORMS["instagram"]["emoji"] == "📷"
    
    def test_linkedin_emoji(self, service):
        """Test LinkedIn emoji."""
        assert service.PLATFORMS["linkedin"]["emoji"] == "💼"
    
    def test_x_emoji(self, service):
        """Test X emoji."""
        assert service.PLATFORMS["x"]["emoji"] == "𝕏"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for the light scan workflow."""
    
    @pytest.fixture
    def service(self):
        """Create a LightScanService instance."""
        return LightScanService()
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_name(self, service):
        """Test full scan workflow with name identifier."""
        result = await service.scan(
            identifier_type="name",
            identifier_value="John Perera",
            location="Sri Lanka"
        )
        
        # Verify structure
        assert result["success"] is True
        assert result["scan_type"] == "light"
        assert result["identifier"]["type"] == "name"
        assert result["identifier"]["value"] == "John Perera"
        assert result["location"] == "Sri Lanka"
        
        # Verify platforms
        assert len(result["platforms"]) == 4
        
        # Verify summary matches platform results
        for platform_data in result["platforms"]:
            platform_id = platform_data["platform"]
            assert result["summary"][platform_id] == platform_data["results_count"]
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_email(self, service):
        """Test full scan workflow with email identifier."""
        result = await service.scan(
            identifier_type="email",
            identifier_value="john@example.com"
        )
        
        # Verify structure
        assert result["success"] is True
        assert result["identifier"]["type"] == "email"
        assert result["identifier"]["value"] == "john@example.com"
        
        # Verify queries were generated for email
        for platform_data in result["platforms"]:
            # Should have queries for both email and extracted username
            assert len(platform_data["queries_used"]) >= 2
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_username(self, service):
        """Test full scan workflow with username identifier."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="john_doe"
        )
        
        # Verify structure
        assert result["success"] is True
        assert result["identifier"]["type"] == "username"
        assert result["identifier"]["value"] == "john_doe"
        
        # Verify queries were generated for variations
        for platform_data in result["platforms"]:
            # Should have queries for multiple variations
            assert len(platform_data["queries_used"]) >= 2
    
    @pytest.mark.asyncio
    async def test_deep_scan_availability_message(self, service):
        """Test that deep scan availability message is present."""
        result = await service.scan(
            identifier_type="username",
            identifier_value="test_user"
        )
        
        assert result["deep_scan_available"] is True
        assert "osint" in result["deep_scan_message"].lower() or "deep scan" in result["deep_scan_message"].lower()
