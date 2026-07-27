package com.ailab.auth;

import jakarta.servlet.FilterChain;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpHeaders;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.context.SecurityContextHolder;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;

class JwtAuthFilterTest {

    @AfterEach
    void clearSecurity() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void blankBearerTokenContinuesWithoutParse() throws Exception {
        JwtService jwtService = mock(JwtService.class);
        JwtAuthFilter filter = new JwtAuthFilter(jwtService);

        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader(HttpHeaders.AUTHORIZATION, "Bearer ");
        MockHttpServletResponse response = new MockHttpServletResponse();
        boolean[] continued = {false};
        FilterChain chain = (req, res) -> continued[0] = true;

        assertDoesNotThrow(() -> filter.doFilter(request, response, chain));
        assertTrue(continued[0]);
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        verify(jwtService, never()).parse(anyString());
    }
}
