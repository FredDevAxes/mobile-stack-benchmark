package dev.devaxes.catalogue
import org.junit.Assert.*
import org.junit.Test

class CatalogueTest {
    private val data =
        listOf(
            Product("p001", "Trail pack 01", "Carry", 1500, "sample", "gear-01"),
            Product("p021", "Trail pack 02", "Carry", 1600, "sample", "gear-01"),
        )

    @Test fun searchIsCaseInsensitiveAndFavoritesPreserveOrder() {
        assertEquals(data, filtered(data, "TRAIL", false, emptySet()))
        assertTrue(filtered(data, "unknown", false, emptySet()).isEmpty())
        assertEquals(listOf(data[0]), filtered(data, "pack", true, setOf("p001")))
        assertEquals("€15.00", data[0].price)
    }
}
