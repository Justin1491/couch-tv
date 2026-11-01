package app.couchtv.launcher

/** Main-thread policy, independent of Android so timing/race behavior can be tested on the JVM. */
class HomeLoadPolicy {
    val budgetMs = 1000L
    private var generation = 0
    private var loading = false
    private var delay = 15000L
    private var recovered: String? = null

    fun start(): Int {
        loading = true
        return ++generation
    }

    fun finished(attempt: Int): Boolean {
        if (!loading || attempt != generation) return false
        loading = false
        delay = 15000L
        return true
    }

    fun expired(attempt: Int): Boolean {
        if (!loading || attempt != generation) return false
        loading = false
        return true
    }

    fun localShown() { loading = false; generation++ }

    fun found(base: String) { recovered = base; delay = 15000L }

    fun takeRecovered(): String? = recovered.also { recovered = null }

    fun retryDelay(): Long = delay.also { delay = (delay * 2).coerceAtMost(300000L) }
}
