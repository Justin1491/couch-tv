package app.couchtv.launcher

import java.io.File
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class OfflineHomeTest {
    @get:Rule val temp = TemporaryFolder()

    private fun page(dir: File, contents: String) {
        dir.mkdirs()
        File(dir, "index.html").writeText(contents)
    }

    @Test fun incompleteDownloadKeepsThePreviousHome() {
        val home = OfflineHome(temp.root)
        page(home.current, "old")
        val staging = File(temp.root, "new").apply { mkdirs() }
        assertFalse(home.promote(staging, mapOf("index.html" to 3L)))
        assertEquals("old", File(home.active()!!, "index.html").readText())
    }

    @Test fun completedDownloadReplacesHomeAndKeepsRollbackCopy() {
        val home = OfflineHome(temp.root)
        page(home.current, "old")
        val staging = File(temp.root, "new")
        page(staging, "new")
        assertTrue(home.promote(staging, mapOf("index.html" to 3L)))
        assertEquals("new", File(home.active()!!, "index.html").readText())
        assertEquals("old", File(home.previous, "index.html").readText())
    }

    @Test fun interruptedPromotionCanStillReadThePreviousDirectory() {
        val home = OfflineHome(temp.root)
        page(home.previous, "old")
        home.current.mkdirs()
        assertEquals(home.previous, home.active())
    }

    @Test fun shortSuccessfulDownloadDoesNotReplaceTheOldHome() {
        val home = OfflineHome(temp.root)
        page(home.current, "old")
        val staging = File(temp.root, "new")
        page(staging, "new")
        File(staging, "app.js").writeText("short")
        assertFalse(home.promote(staging, mapOf("index.html" to 3L, "app.js" to 100L)))
        assertEquals("old", File(home.active()!!, "index.html").readText())
    }
}
