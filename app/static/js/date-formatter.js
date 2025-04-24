/**
 * Tarih formatını güzelleştirmek için yardımcı fonksiyonlar
 */

function formatTurkishDate(dateStr) {
    if (!dateStr) return '--';
    
    const date = new Date(dateStr);
    
    // Tarih formatı: 24 Nisan 2025, 15:30
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('tr-TR', options);
}
