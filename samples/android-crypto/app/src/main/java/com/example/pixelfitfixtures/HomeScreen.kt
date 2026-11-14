package com.example.pixelfitfixtures

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private val CanvasColor = Color(0xFFF8F9FA)
private val Ink = Color(0xFF212529)
private val Accent = Color(0xFF0063F5)
private val Muted = Color(0xFF6C757D)
private data class Coin(val name: String, val symbol: String, val price: String, val change: String)
private val coins = listOf(
    Coin("Bitcoin", "BTC", "₹2,509.75", "+9.77%"),
    Coin("Ethereum", "ETH", "₹2,509.75", "-21.00%"),
    Coin("Band Protocol", "BAND", "₹553.06", "-22.97%"),
    Coin("Cardano", "ADA", "₹105.06", "+16.31%"),
    Coin("TRON", "TRX", "₹5.29", "-16.58%"),
    Coin("Tether", "USDT", "₹73.00", "+0.07%"),
    Coin("Dogecoin", "DOGE", "₹23.39", "+21.00%"),
    Coin("Dogecoin", "DOGE", "₹23.39", "+21.00%")
)

@Composable
fun HomeScreen() {
    Box(Modifier.size(375.dp, 812.dp).background(CanvasColor).clipToBounds()) {
        StatusBar(Modifier.offset(x = 32.dp, y = 15.dp))
        WelcomeCard(Modifier.offset(x = 16.dp, y = 56.dp))
        Column(Modifier.offset(x = 16.dp, y = 229.dp).width(343.dp)) {
            Text("Trending Coins", modifier = Modifier.height(20.dp), color = Ink, fontSize = 20.sp, fontWeight = FontWeight.Bold, lineHeight = 20.sp)
            Spacer(Modifier.height(16.dp))
            coins.forEach { coin ->
                CoinRow(coin)
                Spacer(Modifier.height(8.dp))
            }
        }
        BottomNavigation(Modifier.offset(y = 724.dp))
    }
}

@Composable
internal fun StatusBar(modifier: Modifier = Modifier) {
    Text("9:41", modifier, color = Ink, fontSize = 14.sp, fontWeight = FontWeight.Bold)
}

@Composable
private fun WelcomeCard(modifier: Modifier = Modifier) {
    Box(modifier.size(343.dp, 141.dp).background(Accent, RoundedCornerShape(12.dp))) {
        Text("Welcome Agilan,", Modifier.offset(x = 20.dp, y = 24.dp), color = Color.White, fontSize = 12.sp)
        Text("Make you first Investment today", Modifier.offset(x = 20.dp, y = 47.dp), color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Medium)
        Box(Modifier.offset(x = 20.dp, y = 90.dp).size(92.dp, 31.dp).background(CanvasColor, RoundedCornerShape(4.dp)), contentAlignment = Alignment.Center) {
            Text("Invest Today", color = Accent, fontSize = 12.sp, maxLines = 1)
        }
    }
}

@Composable
private fun CoinRow(coin: Coin) {
    Box(Modifier.size(343.dp, 72.dp).background(Color.White, RoundedCornerShape(8.dp))) {
        CoinLogo(coin.symbol, Modifier.offset(x = 16.dp, y = 16.dp))
        Column(Modifier.offset(x = 68.dp, y = 15.dp)) {
            Text(coin.name, color = Ink, fontSize = 16.sp, lineHeight = 20.sp, maxLines = 1)
            Text(coin.symbol, color = Muted, fontSize = 10.sp, lineHeight = 13.sp, maxLines = 1)
        }
        Column(Modifier.align(Alignment.TopEnd).padding(top = 15.dp, end = 16.dp), horizontalAlignment = Alignment.End) {
            Text(coin.price, color = Ink, fontSize = 16.sp, lineHeight = 20.sp, maxLines = 1)
            Text(coin.change, color = if (coin.change.startsWith("+") && coin.symbol != "ADA") Color(0xFF21BF73) else Color(0xFFD90429), fontSize = 10.sp, lineHeight = 13.sp, maxLines = 1)
        }
    }
}

@Composable
private fun CoinLogo(symbol: String, modifier: Modifier = Modifier) {
    val color = when (symbol) {
        "BTC" -> Color(0xFFF7931A)
        "ETH" -> Color(0xFF627EEA)
        "BAND" -> Color(0xFF526BFF)
        "ADA" -> Color(0xFF0033AD)
        "TRX" -> Color(0xFFED0017)
        "USDT" -> Color(0xFF26A17B)
        else -> Color(0xFFC2A633)
    }
    val label = when (symbol) {
        "BTC" -> "₿"
        "ETH" -> "Ξ"
        "ADA" -> "A"
        "TRX" -> "T"
        "USDT" -> "₮"
        "DOGE" -> "Ð"
        else -> "B"
    }
    Box(modifier.size(40.dp).background(color, CircleShape), contentAlignment = Alignment.Center) {
        Text(label, color = Color.White, fontSize = 23.sp, fontWeight = FontWeight.Bold, maxLines = 1)
    }
}

@Composable
internal fun BottomNavigation(modifier: Modifier = Modifier, selectedIndex: Int = 0) {
    Box(modifier.size(375.dp, 88.dp).background(Color.White)) {
        listOf("Home", "Portfolio", "Rewards", "Market", "Profile").forEachIndexed { index, label ->
            val left = listOf(41, 101, 172, 243, 308)[index]
            val width = listOf(28, 39, 39, 33, 30)[index]
            Text(label, Modifier.offset(x = left.dp, y = 41.5.dp).width(width.dp), color = if (index == selectedIndex) Accent else Muted, fontSize = 10.sp, textAlign = TextAlign.Center, maxLines = 1)
        }
        Box(Modifier.offset(x = 121.dp, y = 75.dp).size(134.dp, 5.dp).background(Color.Black, RoundedCornerShape(50)))
    }
}
