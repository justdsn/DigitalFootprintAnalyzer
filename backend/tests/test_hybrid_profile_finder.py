# =============================================================================
# TESTS FOR GOOGLE DORKER AND HYBRID PROFILE FINDER
# =============================================================================
# Tests for the hybrid profile discovery functionality.
# =============================================================================

"""
Test Suite for Google Dorker and Hybrid Profile Finder

Tests cover:
- GoogleDorkSearcher: Search query generation for all identifier types
- HybridProfileFinder: Username generation and profile finding
- URL filtering and validation
- Sri Lankan phone number format handling
"""

import pytest
import asyncio
from app.services.social.google_dorker import GoogleDorkSearcher
from app.services.social.profile_finder import HybridProfileFinder


# =============================================================================
# GOOGLE DORK SEARCHER TESTS
# =============================================================================

class TestGoogleDorkSearcher:
    """Tests for GoogleDorkSearcher class."""
    
    @pytest.fixture
    def searcher(self):
        """Create a GoogleDorkSearcher instance."""
        return GoogleDorkSearcher()
    
    # -------------------------------------------------------------------------
    # SEARCH BY USERNAME TESTS
    # -------------------------------------------------------------------------
    
    def test_search_by_username_returns_results(self, searcher):
        """Test that username search returns results for all platforms."""
        results = searcher.search_by_username("john_doe")
        assert len(results) > 0
    
    def test_search_by_username_includes_all_platforms(self, searcher):
        """Test that username search includes all supported platforms."""
        results = searcher.search_by_username("john_doe")
        platforms = {r["platform_id"] for r in results}
        # Should include facebook, instagram, linkedin, x
        assert "facebook" in platforms
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "x" in platforms
    
    def test_search_by_username_generates_variations(self, searcher):
        """Test that username search generates username variations."""
        results = searcher.search_by_username("john_doe")
        identifiers = {r["identifier"] for r in results}
        # Should include variations like john_doe, johndoe, john.doe
        assert "john_doe" in identifiers
        assert "johndoe" in identifiers
    
    def test_search_by_username_strips_at_symbol(self, searcher):
        """Test that @ symbol is stripped from usernames."""
        results = searcher.search_by_username("@john_doe")
        identifiers = {r["identifier"] for r in results}
        assert "john_doe" in identifiers
        assert "@john_doe" not in identifiers
    
    def test_search_by_empty_username_returns_empty(self, searcher):
        """Test that empty username returns empty list."""
        assert searcher.search_by_username("") == []
        assert searcher.search_by_username("  ") == []
    
    # -------------------------------------------------------------------------
    # SEARCH BY NAME TESTS
    # -------------------------------------------------------------------------
    
    def test_search_by_name_returns_results(self, searcher):
        """Test that name search returns results."""
        results = searcher.search_by_name("John Perera")
        assert len(results) == 4  # One per platform
    
    def test_search_by_name_includes_location(self, searcher):
        """Test that name search includes location filter."""
        results = searcher.search_by_name("John Perera", "Colombo")
        for result in results:
            assert "Colombo" in result["query"]
    
    def test_search_by_name_default_location_sri_lanka(self, searcher):
        """Test that default location is Sri Lanka."""
        results = searcher.search_by_name("John Perera")
        for result in results:
            assert "Sri Lanka" in result["query"]
    
    def test_search_by_name_no_location(self, searcher):
        """Test name search without location filter."""
        results = searcher.search_by_name("John Perera", None)
        for result in results:
            assert "Sri Lanka" not in result["query"]
    
    def test_search_by_empty_name_returns_empty(self, searcher):
        """Test that empty name returns empty list."""
        assert searcher.search_by_name("") == []
    
    # -------------------------------------------------------------------------
    # SEARCH BY EMAIL TESTS
    # -------------------------------------------------------------------------
    
    def test_search_by_email_returns_results(self, searcher):
        """Test that email search returns results."""
        results = searcher.search_by_email("john@gmail.com")
        assert len(results) > 0
    
    def test_search_by_email_extracts_username(self, searcher):
        """Test that email search extracts username portion."""
        results = searcher.search_by_email("john.perera@gmail.com")
        identifiers = {r["identifier"] for r in results}
        assert "john.perera" in identifiers
    
    def test_search_by_email_searches_full_email(self, searcher):
        """Test that email search also searches full email."""
        results = searcher.search_by_email("john@gmail.com")
        identifiers = {r["identifier"] for r in results}
        assert "john@gmail.com" in identifiers
    
    def test_search_by_invalid_email_returns_empty(self, searcher):
        """Test that invalid email returns empty list."""
        assert searcher.search_by_email("not_an_email") == []
        assert searcher.search_by_email("missing@domain") == []
    
    def test_search_by_empty_email_returns_empty(self, searcher):
        """Test that empty email returns empty list."""
        assert searcher.search_by_email("") == []
    
    # -------------------------------------------------------------------------
    # SEARCH BY PHONE TESTS
    # -------------------------------------------------------------------------
    
    def test_search_by_phone_returns_results(self, searcher):
        """Test that phone search returns results."""
        results = searcher.search_by_phone("0771234567")
        assert len(results) > 0
    
    def test_search_by_phone_generates_sri_lankan_formats(self, searcher):
        """Test that phone search generates Sri Lankan format variations."""
        results = searcher.search_by_phone("0771234567")
        identifiers = {r["identifier"] for r in results}
        # Should include various formats
        assert "0771234567" in identifiers
        assert "+94771234567" in identifiers
    
    def test_search_by_phone_international_format(self, searcher):
        """Test phone search with international format input."""
        results = searcher.search_by_phone("+94771234567")
        identifiers = {r["identifier"] for r in results}
        # Should still include local format
        assert "0771234567" in identifiers
    
    def test_search_by_phone_formatted_input(self, searcher):
        """Test phone search with formatted input."""
        results = searcher.search_by_phone("077-123-4567")
        identifiers = {r["identifier"] for r in results}
        # Should handle formatted input
        assert len(identifiers) > 0
    
    def test_search_by_empty_phone_returns_empty(self, searcher):
        """Test that empty phone returns empty list."""
        assert searcher.search_by_phone("") == []
    
    # -------------------------------------------------------------------------
    # URL FILTERING TESTS
    # -------------------------------------------------------------------------
    
    def test_is_profile_url_accepts_valid_profiles(self, searcher):
        """Test that valid profile URLs are accepted."""
        assert searcher.is_profile_url("https://facebook.com/john_doe")
        assert searcher.is_profile_url("https://instagram.com/john_doe/")
        assert searcher.is_profile_url("https://linkedin.com/in/john-doe")
        assert searcher.is_profile_url("https://x.com/johndoe")
    
    def test_is_profile_url_rejects_search_pages(self, searcher):
        """Test that search pages are rejected."""
        assert not searcher.is_profile_url("https://facebook.com/search?q=john")
        assert not searcher.is_profile_url("https://instagram.com/explore")
    
    def test_is_profile_url_rejects_help_pages(self, searcher):
        """Test that help/support pages are rejected."""
        assert not searcher.is_profile_url("https://facebook.com/help")
        assert not searcher.is_profile_url("https://instagram.com/support")
    
    def test_is_profile_url_rejects_login_pages(self, searcher):
        """Test that login pages are rejected."""
        assert not searcher.is_profile_url("https://facebook.com/login")
        assert not searcher.is_profile_url("https://instagram.com/signup")
    
    def test_extract_username_from_url(self, searcher):
        """Test username extraction from profile URLs."""
        assert searcher.extract_username_from_url(
            "https://facebook.com/john_doe", "facebook"
        ) == "john_doe"
        assert searcher.extract_username_from_url(
            "https://instagram.com/john.doe/", "instagram"
        ) == "john.doe"
    
    # -------------------------------------------------------------------------
    # HELPER METHOD TESTS
    # -------------------------------------------------------------------------
    
    def test_get_supported_platforms(self, searcher):
        """Test that supported platforms are returned."""
        platforms = searcher.get_supported_platforms()
        assert "facebook" in platforms
        assert "instagram" in platforms
        assert "linkedin" in platforms
        assert "x" in platforms
    
    def test_build_combined_dork_query(self, searcher):
        """Test combined dork query building."""
        query = searcher.build_combined_dork_query("john_doe", "username")
        assert "site:facebook.com" in query
        assert "site:instagram.com" in query
        assert '"john_doe"' in query


# =============================================================================
# HYBRID PROFILE FINDER TESTS
# =============================================================================

class TestHybridProfileFinder:
    """Tests for HybridProfileFinder class."""
    
    @pytest.fixture
    def finder(self):
        """Create a HybridProfileFinder instance."""
        return HybridProfileFinder()
    
    # -------------------------------------------------------------------------
    # USERNAME GENERATION FROM NAME TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_usernames_from_name(self, finder):
        """Test username generation from a full name."""
        usernames = finder._generate_usernames_from_name("John Perera")
        assert "john" in usernames
        assert "perera" in usernames
        assert "johnperera" in usernames
        assert "john_perera" in usernames
        assert "john.perera" in usernames
        assert "jperera" in usernames  # first initial + last name
    
    def test_generate_usernames_from_single_name(self, finder):
        """Test username generation from single name."""
        usernames = finder._generate_usernames_from_name("John")
        assert "john" in usernames
    
    def test_generate_usernames_from_name_with_suffixes(self, finder):
        """Test that common suffixes are added."""
        usernames = finder._generate_usernames_from_name("John Perera")
        # Should include some common suffixes
        assert any("123" in u for u in usernames)
    
    def test_generate_usernames_from_empty_name(self, finder):
        """Test that empty name returns empty list."""
        assert finder._generate_usernames_from_name("") == []
        assert finder._generate_usernames_from_name("  ") == []
    
    # -------------------------------------------------------------------------
    # USERNAME GENERATION FROM EMAIL TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_usernames_from_email(self, finder):
        """Test username generation from email."""
        usernames = finder._generate_usernames_from_email("john.perera@gmail.com")
        assert "john.perera" in usernames
        assert "johnperera" in usernames
        assert "john_perera" in usernames
    
    def test_generate_usernames_from_invalid_email(self, finder):
        """Test that invalid email returns empty list."""
        assert finder._generate_usernames_from_email("not_an_email") == []
    
    def test_generate_usernames_from_empty_email(self, finder):
        """Test that empty email returns empty list."""
        assert finder._generate_usernames_from_email("") == []
    
    # -------------------------------------------------------------------------
    # USERNAME VARIATIONS TESTS
    # -------------------------------------------------------------------------
    
    def test_generate_username_variations(self, finder):
        """Test username variation generation."""
        variations = finder._generate_username_variations("john_doe")
        assert "john_doe" in variations
        assert "johndoe" in variations
        assert "john.doe" in variations
        assert "_john_doe" in variations
        assert "john_doe_" in variations
    
    def test_generate_username_variations_strips_at(self, finder):
        """Test that @ is stripped from username."""
        variations = finder._generate_username_variations("@john_doe")
        assert "john_doe" in variations
        assert "@john_doe" not in variations
    
    # -------------------------------------------------------------------------
    # PROFILE FINDING TESTS (ASYNC)
    # -------------------------------------------------------------------------
    
    @pytest.mark.asyncio
    async def test_find_profiles_returns_result_structure(self, finder):
        """Test that find_profiles returns correct structure."""
        # Disable existence checking for faster test
        result = await finder.find_profiles(
            "john_doe", "username", check_existence=False
        )
        
        assert "identifier" in result
        assert "identifier_type" in result
        assert "timestamp" in result
        assert "dork_results" in result
        assert "combined_results" in result
        assert "username_variations" in result
        assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_find_profiles_by_username(self, finder):
        """Test profile finding by username."""
        result = await finder.find_profiles(
            "john_doe", "username", check_existence=False
        )
        
        assert result["identifier"] == "john_doe"
        assert result["identifier_type"] == "username"
        assert len(result["dork_results"]) > 0
        assert len(result["username_variations"]) > 0
    
    @pytest.mark.asyncio
    async def test_find_profiles_by_email(self, finder):
        """Test profile finding by email."""
        result = await finder.find_profiles(
            "john@gmail.com", "email", check_existence=False
        )
        
        assert result["identifier"] == "john@gmail.com"
        assert result["identifier_type"] == "email"
        assert len(result["dork_results"]) > 0
        # Should extract username from email
        assert "john" in result["username_variations"]
    
    @pytest.mark.asyncio
    async def test_find_profiles_by_name(self, finder):
        """Test profile finding by name."""
        result = await finder.find_profiles(
            "John Perera", "name", check_existence=False
        )
        
        assert result["identifier"] == "John Perera"
        assert result["identifier_type"] == "name"
        assert result["location_filter"] == "Sri Lanka"  # Default
        assert len(result["username_variations"]) > 0
    
    @pytest.mark.asyncio
    async def test_find_profiles_by_phone(self, finder):
        """Test profile finding by phone."""
        result = await finder.find_profiles(
            "0771234567", "phone", check_existence=False
        )
        
        assert result["identifier"] == "0771234567"
        assert result["identifier_type"] == "phone"
        assert len(result["dork_results"]) > 0
        # Phone doesn't generate username variations
        assert result["username_variations"] == []
    
    @pytest.mark.asyncio
    async def test_find_profiles_with_custom_location(self, finder):
        """Test profile finding with custom location."""
        result = await finder.find_profiles(
            "John Perera", "name", location="Colombo", check_existence=False
        )
        
        assert result["location_filter"] == "Colombo"
        # Check that Colombo appears in dork queries
        dork_queries = [d["query"] for d in result["dork_results"]]
        assert any("Colombo" in q for q in dork_queries)
    
    @pytest.mark.asyncio
    async def test_find_profiles_empty_identifier(self, finder):
        """Test that empty identifier returns empty result."""
        result = await finder.find_profiles(
            "", "username", check_existence=False
        )
        
        assert result["summary"]["total_profiles_found"] == 0
        assert result["dork_results"] == []
    
    @pytest.mark.asyncio
    async def test_find_profiles_summary_structure(self, finder):
        """Test that summary has correct structure."""
        result = await finder.find_profiles(
            "john_doe", "username", check_existence=False
        )
        
        summary = result["summary"]
        assert "total_profiles_found" in summary
        assert "platforms_with_profiles" in summary
        assert "total_platforms_checked" in summary
        assert "total_search_queries" in summary
        assert "usernames_checked" in summary


# =============================================================================
# PHONE NUMBER FORMAT TESTS
# =============================================================================

class TestPhoneNumberFormats:
    """Tests for Sri Lankan phone number format handling."""
    
    @pytest.fixture
    def searcher(self):
        """Create a GoogleDorkSearcher instance."""
        return GoogleDorkSearcher()
    
    def test_local_mobile_format(self, searcher):
        """Test local mobile format (07XXXXXXXX)."""
        variations = searcher._generate_phone_variations("0771234567")
        assert "0771234567" in variations
        assert "+94771234567" in variations
    
    def test_international_format_with_plus(self, searcher):
        """Test international format (+947XXXXXXXX)."""
        variations = searcher._generate_phone_variations("+94771234567")
        assert "0771234567" in variations
        assert "+94771234567" in variations
    
    def test_international_format_without_plus(self, searcher):
        """Test international format without + (947XXXXXXXX)."""
        variations = searcher._generate_phone_variations("94771234567")
        assert "0771234567" in variations
        assert "+94771234567" in variations
    
    def test_international_format_00(self, searcher):
        """Test international format with 00 prefix."""
        variations = searcher._generate_phone_variations("0094771234567")
        assert "0771234567" in variations
        assert "+94771234567" in variations
    
    def test_formatted_local_variations(self, searcher):
        """Test that formatted local variations are generated."""
        variations = searcher._generate_phone_variations("0771234567")
        assert "077-123-4567" in variations
        assert "077 123 4567" in variations
    
    def test_formatted_international_variations(self, searcher):
        """Test that formatted international variations are generated."""
        variations = searcher._generate_phone_variations("0771234567")
        assert "+94 77 123 4567" in variations


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for the hybrid profile discovery system."""
    
    @pytest.fixture
    def finder(self):
        """Create a HybridProfileFinder instance."""
        return HybridProfileFinder()
    
    @pytest.mark.asyncio
    async def test_full_workflow_username(self, finder):
        """Test full workflow with username identifier."""
        result = await finder.find_profiles(
            "test_user_123", "username", check_existence=False
        )
        
        # Verify structure
        assert result["identifier"] == "test_user_123"
        assert result["identifier_type"] == "username"
        
        # Verify dork results
        assert len(result["dork_results"]) > 0
        for dork in result["dork_results"]:
            assert "platform" in dork
            assert "query" in dork
            assert "search_url" in dork
        
        # Verify combined results structure
        combined = result["combined_results"]
        assert "by_platform" in combined
        assert "search_queries" in combined
    
    @pytest.mark.asyncio
    async def test_full_workflow_name(self, finder):
        """Test full workflow with name identifier."""
        result = await finder.find_profiles(
            "Sunil Perera", "name", location="Kandy", check_existence=False
        )
        
        # Verify name-based username generation
        usernames = result["username_variations"]
        assert "sunil" in usernames
        assert "perera" in usernames
        assert "sunilperera" in usernames
        
        # Verify location filter in queries
        dork_queries = [d["query"] for d in result["dork_results"]]
        assert any("Kandy" in q for q in dork_queries)
