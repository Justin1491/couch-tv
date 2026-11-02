package app.couchtv.launcher

import java.io.File

/** Keep a usable previous directory across failed or interrupted promotions. */
class OfflineHome(root: File) {
    val current = File(root, "web")
    val previous = File(root, "previous")

    fun active(): File? = listOf(current, previous).firstOrNull { File(it, "index.html").isFile }

    fun promote(staging: File, expectedFiles: Map<String, Long>): Boolean {
        if ("index.html" !in expectedFiles || expectedFiles.any { (path, size) ->
                path.contains("..") || File(path).isAbsolute || size < 0 ||
                    !File(staging, path).isFile || File(staging, path).length() != size
            }) return false
        if (File(current, "index.html").isFile) {
            if (previous.exists() && !previous.deleteRecursively()) return false
            if (!current.renameTo(previous)) return false
        } else if (current.exists() && !current.deleteRecursively()) return false
        if (staging.renameTo(current)) return true
        if (!current.exists()) previous.renameTo(current)
        return false
    }
}
