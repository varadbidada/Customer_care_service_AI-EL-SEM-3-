# Shop at RVCE Chatbot - Demo Questions Guide 🎯

## Quick Action Buttons (Click These First!)

### 🎯 **Built-in Quick Actions**

These are the 6 buttons that appear when you first open the chat:

1. **📦 Track Order** - "Track my order"
2. **↩️ Return Item** - "I want to return an item"
3. **💳 Billing Help** - "I have a billing issue"
4. **📚 Find Books** - "Show me textbooks"
5. **📍 Delivery Info** - "Campus delivery options"
6. **💰 Discounts** - "Student discount available?"

---

## Order Tracking & Management

### 📦 **Order Status Queries**

```
"What's the status of my order?"
"Track order 12345"
"Where is my order #54582?"
"I want to check my order status"
"Has my order been shipped?"
"When will my order arrive?"
```

### 📋 **Order Information**

```
"Show me my recent orders"
"I need details about order 16399"
"What did I order last week?"
"Can you find my order with phone number?"
"I forgot my order number"
```

---

## Billing & Payment Issues

### 💳 **Payment Problems**

```
"I have a billing issue"
"My payment failed"
"I was charged twice"
"Refund not received"
"Payment method declined"
"I need a receipt"
```

### 💰 **Refund Queries**

```
"I didn't get my refund"
"How long does refund take?"
"Refund status for order 16399"
"Cancel my order and refund"
"Partial refund request"
```

---

## Product & Shopping Queries

### 📚 **Academic Items**

```
"Show me engineering textbooks"
"I need computer science books"
"Do you have lab manuals?"
"Stationery items available?"
"Scientific calculator price?"
"Drawing instruments for engineering"
```

### 💻 **Electronics**

```
"Laptop deals for students"
"Headphones under 3000"
"Phone accessories available"
"Charging cables in stock?"
"Bluetooth speakers price"
"Gaming mouse recommendations"
```

### 👕 **Campus Fashion**

```
"RVCE t-shirts available?"
"College merchandise"
"Hoodies with college logo"
"Sports wear for students"
"Formal shirts for placements"
```

---

## Campus-Specific Services

### 🚚 **Delivery & Logistics**

```
"Campus delivery options"
"Hostel delivery available?"
"Delivery timings on campus"
"Same day delivery possible?"
"Delivery charges to hostel"
"Pick up from campus store"
```

### 🎓 **Student Services**

```
"Student discount available?"
"Bulk order for class?"
"Group purchase discount"
"Semester book packages"
"Lab equipment rental"
"Exam supplies bundle"
```

---

## Technical Support

### 🔧 **General Issues**

```
"I can't login to my account"
"Website not working properly"
"App crashing frequently"
"Password reset help"
"Account verification issue"
```

### 📱 **Mobile App Problems**

```
"App won't open"
"Payment not going through on app"
"Notifications not working"
"App update issues"
"Slow loading on mobile"
```

---

## Returns & Exchanges

### ↩️ **Return Requests**

```
"I want to return this item"
"Return policy for textbooks"
"Exchange size for t-shirt"
"Defective product return"
"Wrong item delivered"
"Return pickup from hostel"
```

### 🔄 **Exchange Queries**

```
"Exchange for different color"
"Size exchange possible?"
"Book edition exchange"
"Damaged item replacement"
"Exchange within warranty"
```

---

## Complex Multi-Turn Conversations

### 🎯 **Scenario 1: Order Issue Resolution**

```
1. "I have a problem with my order"
2. [Bot asks for order number]
3. "Order number is 54582"
4. [Bot shows order details]
5. "The item is damaged"
6. [Bot offers return/exchange options]
```

### 🎯 **Scenario 2: Billing Investigation**

```
1. "I was charged but didn't receive my order"
2. [Bot asks for order details]
3. "Order 16399, paid ₹2999"
4. [Bot checks payment and order status]
5. "When will I get my refund?"
6. [Bot explains refund process]
```

### 🎯 **Scenario 3: Product Recommendation**

```
1. "I need a laptop for engineering"
2. [Bot asks about budget and requirements]
3. "Budget is 50000, need for coding"
4. [Bot suggests options]
5. "What about warranty?"
6. [Bot explains warranty terms]
```

---

## Edge Cases & Error Handling

### ❌ **Invalid Inputs**

```
"Order number xyz123" (invalid format)
"Refund for order that doesn't exist"
"Track order without providing number"
"Return item after return period"
```

### 🔍 **Unclear Requests**

```
"Help me"
"I have a problem"
"Something is wrong"
"Fix this"
"Not working"
```

---

## Voice & Interactive Features

### 🎤 **Voice Input Tests**

- Click the microphone button and speak any of the above queries
- Test with different accents and speaking speeds
- Try background noise scenarios

### 🔊 **Text-to-Speech Tests**

- Toggle the speaker button to enable/disable voice responses
- Test with long and short responses
- Check voice quality and clarity

---

## Demo Flow Suggestions

### 🎬 **5-Minute Demo Script**

#### **Opening (30 seconds)**

1. Open http://localhost:5000/ecommerce
2. Show the Shop at RVCE homepage
3. Point out the orange chat button

#### **Basic Functionality (1 minute)**

1. Click chat button to open
2. Show SupportX AI interface
3. Click "Track Order" quick action
4. Demonstrate order lookup

#### **Advanced Features (2 minutes)**

1. Type: "I have a billing issue with order 16399"
2. Show multi-turn conversation
3. Demonstrate voice input (click microphone)
4. Test voice output (toggle speaker)

#### **Campus Features (1 minute)**

1. Ask: "Show me engineering textbooks"
2. Try: "Student discount available?"
3. Test: "Campus delivery options"

#### **Error Handling (30 seconds)**

1. Try invalid order number
2. Show graceful error handling
3. Demonstrate fallback responses

---

## Expected Responses

### ✅ **What Should Work**

- Order tracking with valid order numbers (12345, 54582, 16399, etc.)
- Billing issue resolution with context preservation
- Product searches and recommendations
- Campus-specific service information
- Multi-turn conversations with memory
- Voice input and output features

### ⚠️ **Known Limitations**

- Some advanced ML features may have limited responses
- Voice recognition depends on browser support
- TTS quality varies by system
- Complex product catalogs are simulated

---

## Pro Tips for Demo

### 🎯 **Best Practices**

1. **Start with Quick Actions** - They always work reliably
2. **Use Valid Order Numbers** - 12345, 54582, 16399 are in the dataset
3. **Test Voice Features** - Great for showing modern capabilities
4. **Show Mobile Responsiveness** - Resize browser window
5. **Demonstrate Error Recovery** - Show robust error handling

### 🚀 **Impressive Features to Highlight**

- **Real-time responses** with typing indicators
- **Context preservation** across conversation turns
- **Campus-specific branding** and content
- **Voice interaction** capabilities
- **Professional UI/UX** design
- **Mobile-responsive** layout

---

**Ready to Demo!** 🎉

Use these questions to showcase the full capabilities of your Shop at RVCE chatbot. Start with the quick actions, then move to more complex scenarios to demonstrate the AI's conversational abilities!
