package app.couchtv.launcher

import org.junit.Assert.*
import org.junit.Test

class HomeLoadPolicyTest {
    @Test fun deadlineRejectsLateServerCompletion() {
        val p = HomeLoadPolicy()
        val attempt = p.start()
        assertEquals(1000L, p.budgetMs)
        assertTrue(p.expired(attempt))
        assertFalse(p.finished(attempt))
    }

    @Test fun fastServerCancelsFallbackAndOlderTimersCannotWin() {
        val p = HomeLoadPolicy()
        val old = p.start()
        val current = p.start()
        assertFalse(p.expired(old))
        assertTrue(p.finished(current))
        assertFalse(p.expired(current))
    }

    @Test fun recoveredServerIsOnlyConsumedAtHomeTransition() {
        val p = HomeLoadPolicy()
        p.found("http://server:5400")
        assertEquals("http://server:5400", p.takeRecovered())
        assertNull(p.takeRecovered())
    }

    @Test fun retriesBackOffAndResetOnSuccess() {
        val p = HomeLoadPolicy()
        assertEquals(listOf(15000L, 30000L, 60000L, 120000L, 240000L, 300000L, 300000L),
            (1..7).map { p.retryDelay() })
        p.found("http://server:5400")
        assertEquals(15000L, p.retryDelay())
    }
}
