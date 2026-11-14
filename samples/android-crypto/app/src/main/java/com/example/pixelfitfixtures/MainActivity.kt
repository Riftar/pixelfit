package com.example.pixelfitfixtures
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.WindowManager
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN)
        if (intent.getStringExtra("screen") == "rewards_xml") {
            showRewardsXml()
        } else if (intent.getStringExtra("screen") == "rewards_compose") {
            setContent { RewardsScreen() }
        } else if (intent.getStringExtra("screen") == "xml") {
            setContentView(R.layout.home_screen)
            val list = findViewById<LinearLayout>(R.id.coin_list)
            val coins = listOf(
                listOf("Bitcoin", "BTC", "₹2,509.75", "+9.77%"),
                listOf("Ethereum", "ETH", "₹2,509.75", "-21.00%"),
                listOf("Band Protocol", "BAND", "₹553.06", "-22.97%"),
                listOf("Cardano", "ADA", "₹105.06", "+16.31%"),
                listOf("TRON", "TRX", "₹5.29", "-16.58%"),
                listOf("Tether", "USDT", "₹73.00", "+0.07%"),
                listOf("Dogecoin", "DOGE", "₹23.39", "+21.00%"),
                listOf("Dogecoin", "DOGE", "₹23.39", "+21.00%")
            )
            coins.forEach { coin ->
                val row = LayoutInflater.from(this).inflate(R.layout.coin_row, list, false)
                val logoColor = when (coin[1]) {
                    "BTC" -> "#F7931A"
                    "ETH" -> "#627EEA"
                    "BAND" -> "#526BFF"
                    "ADA" -> "#0033AD"
                    "TRX" -> "#ED0017"
                    "USDT" -> "#26A17B"
                    else -> "#C2A633"
                }
                val logoText = when (coin[1]) {
                    "BTC" -> "₿"
                    "ETH" -> "Ξ"
                    "ADA" -> "A"
                    "TRX" -> "T"
                    "USDT" -> "₮"
                    "DOGE" -> "Ð"
                    else -> "B"
                }
                row.findViewById<TextView>(R.id.coin_logo).apply {
                    text = logoText
                    background = GradientDrawable().apply {
                        shape = GradientDrawable.OVAL
                        setColor(Color.parseColor(logoColor))
                    }
                }
                row.findViewById<TextView>(R.id.coin_name).text = coin[0]
                row.findViewById<TextView>(R.id.coin_symbol).text = coin[1]
                row.findViewById<TextView>(R.id.coin_price).text = coin[2]
                row.findViewById<TextView>(R.id.coin_change).apply {
                    text = coin[3]
                    setTextColor(Color.parseColor(if (coin[3].startsWith("+") && coin[1] != "ADA") "#21BF73" else "#D90429"))
                }
                list.addView(row)
            }
        } else {
            setContent { HomeScreen() }
        }
    }
}