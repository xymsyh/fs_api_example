package com.example.texttransformer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.tooling.preview.Preview

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.texttransformer.ui.theme.TextTransformerTheme
import androidx.compose.foundation.text.BasicTextField
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.*


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TextTransformerTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    TextTransformerApp()
                }
            }
        }
    }
}

@Composable
fun TextTransformerApp() {
    val context = LocalContext.current
    var text by remember { mutableStateOf("") }
    var result by remember { mutableStateOf("") }
    val clipboardManager = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager

    // Layout
    Column(modifier = Modifier.padding(16.dp)) {
        BasicTextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.padding(16.dp)
        )
        Button(
            onClick = {
                result = "[$text[]$text]"
                // 实现复制到剪贴板的逻辑
                val clip = ClipData.newPlainText("label", result)
                clipboardManager.setPrimaryClip(clip)
            },
            modifier = Modifier.padding(16.dp)
        ) {
            Text("Transform")
        }
        BasicTextField(
            value = result,
            onValueChange = { /* Do nothing with input here */ },
            modifier = Modifier.padding(16.dp)
        )
    }
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    TextTransformerTheme {
        TextTransformerApp()
    }
}
