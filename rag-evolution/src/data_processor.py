import chromadb
from openai import OpenAI
from typing import List, Dict
from pyprojroot import here
from load_config import APPConfig

# Load application configuration
APP_CONFIG = APPConfig().load()


# Configure OpenAI Client - using the same pattern as your working file
client = OpenAI()  # Will use OPENAI_API_KEY from environment


class DataPrep:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(here(APP_CONFIG.chroma_db_path)))

    def _get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text using latest model"""
        try:
            response = client.embeddings.create(
                model=APP_CONFIG.embedding_model,  # Latest embedding model
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    def _create_tech_docs_dataset(self) -> List[Dict]:
        """Create technical documentation dataset"""
        return [
            {
                "id": "tech_001",
                "content": "Python is a high-level, interpreted programming language with dynamic semantics. Its high-level built-in data structures, combined with dynamic typing and dynamic binding, make it very attractive for Rapid Application Development, as well as for use as a scripting or glue language to connect existing components together.",
                "metadata": {"category": "python_basics", "type": "intro", "difficulty": "beginner"}
            },
            {
                "id": "tech_002",
                "content": "Machine Learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. ML focuses on the development of computer programs that can access data and use it to learn for themselves.",
                "metadata": {"category": "machine_learning", "type": "definition", "difficulty": "beginner"}
            },
            {
                "id": "tech_003",
                "content": "Neural networks are computing systems vaguely inspired by the biological neural networks that constitute animal brains. A neural network is based on a collection of connected units or nodes called artificial neurons, which loosely model the neurons in a biological brain.",
                "metadata": {"category": "deep_learning", "type": "concept", "difficulty": "intermediate"}
            },
            {
                "id": "tech_004",
                "content": "REST (Representational State Transfer) is an architectural style for designing networked applications. REST relies on a stateless, client-server, cacheable communications protocol. RESTful applications use HTTP requests to post data (create/update), read data (make queries), and delete data.",
                "metadata": {"category": "web_development", "type": "architecture", "difficulty": "intermediate"}
            },
            {
                "id": "tech_005",
                "content": "Docker is a platform that uses OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries and configuration files; they can communicate with each other through well-defined channels.",
                "metadata": {"category": "devops", "type": "tool", "difficulty": "intermediate"}
            },
            {
                "id": "tech_006",
                "content": "Git is a distributed version control system for tracking changes in source code during software development. It is designed for coordinating work among programmers, but it can be used to track changes in any set of files. Git emphasizes speed, data integrity, and support for distributed, non-linear workflows.",
                "metadata": {"category": "version_control", "type": "tool", "difficulty": "beginner"}
            },
            {
                "id": "tech_007",
                "content": "API (Application Programming Interface) is a set of protocols, routines, and tools for building software applications. APIs specify how software components should interact and are used when programming graphical user interface (GUI) components.",
                "metadata": {"category": "programming", "type": "concept", "difficulty": "beginner"}
            },
            {
                "id": "tech_008",
                "content": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It groups containers that make up an application into logical units for easy management and discovery.",
                "metadata": {"category": "devops", "type": "orchestration", "difficulty": "advanced"}
            },
            {
                "id": "tech_009",
                "content": "TensorFlow is an open-source machine learning framework developed by Google. It provides a comprehensive ecosystem of tools, libraries, and community resources that lets researchers and developers build and deploy ML-powered applications easily.",
                "metadata": {"category": "machine_learning", "type": "framework", "difficulty": "intermediate"}
            },
            {
                "id": "tech_010",
                "content": "NoSQL databases are non-relational databases that provide flexible schemas for the storage and retrieval of data. They are particularly useful for working with large sets of distributed data and are designed to scale out by using many commodity servers.",
                "metadata": {"category": "database", "type": "concept", "difficulty": "intermediate"}
            },
            {
                "id": "tech_011",
                "content": "Microservices architecture is a method of developing software systems that focuses on building single-function modules with well-defined interfaces and operations. These modules can be independently deployed and operated by small teams that own the entire lifecycle.",
                "metadata": {"category": "architecture", "type": "pattern", "difficulty": "advanced"}
            },
            {
                "id": "tech_012",
                "content": "GraphQL is a query language and runtime for APIs that allows clients to request exactly the data they need. It provides a complete description of the data in your API, gives clients the power to ask for exactly what they need, and makes it easier to evolve APIs over time.",
                "metadata": {"category": "api", "type": "query_language", "difficulty": "intermediate"}
            },
            {
                "id": "tech_013",
                "content": "DevOps is a set of practices that combines software development (Dev) and IT operations (Ops). It aims to shorten the systems development life cycle and provide continuous delivery with high software quality through automation and monitoring.",
                "metadata": {"category": "methodology", "type": "practice", "difficulty": "intermediate"}
            },
            {
                "id": "tech_014",
                "content": "Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet (the cloud) to offer faster innovation, flexible resources, and economies of scale.",
                "metadata": {"category": "cloud", "type": "concept", "difficulty": "beginner"}
            },
            {
                "id": "tech_015",
                "content": "Agile is a project management and software development approach that emphasizes flexibility, collaboration, and customer satisfaction. It involves breaking down large projects into smaller, manageable tasks that can be completed in short iterations called sprints.",
                "metadata": {"category": "methodology", "type": "framework", "difficulty": "beginner"}
            },
            {
                "id": "tech_016",
                "content": "Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data.",
                "metadata": {"category": "blockchain", "type": "technology", "difficulty": "advanced"}
            },
            {
                "id": "tech_017",
                "content": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.",
                "metadata": {"category": "ai", "type": "definition", "difficulty": "beginner"}
            },
            {
                "id": "tech_018",
                "content": "Big Data refers to extremely large datasets that may be analyzed computationally to reveal patterns, trends, and associations. It is characterized by the three Vs: Volume (large amounts of data), Velocity (fast data processing), and Variety (different types of data).",
                "metadata": {"category": "data_science", "type": "concept", "difficulty": "intermediate"}
            },
            {
                "id": "tech_019",
                "content": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These attacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes.",
                "metadata": {"category": "security", "type": "practice", "difficulty": "intermediate"}
            },
            {
                "id": "tech_020",
                "content": "Internet of Things (IoT) describes the network of physical objects that are embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the internet.",
                "metadata": {"category": "iot", "type": "technology", "difficulty": "intermediate"}
            }
        ]

    def _create_faq_dataset(self) -> List[Dict]:
        """Create FAQ dataset"""
        return [
            {
                "id": "faq_001",
                "content": "Q: What is your return policy? A: We offer a 30-day return policy for all items. Items must be returned in original condition with receipt. Refunds will be processed within 5-7 business days after we receive the returned item.",
                "metadata": {"category": "returns", "type": "policy", "priority": "high"}
            },
            {
                "id": "faq_002",
                "content": "Q: How long does shipping take? A: Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days. International shipping takes 7-14 business days depending on location. Tracking information is provided once your order ships.",
                "metadata": {"category": "shipping", "type": "timeline", "priority": "high"}
            },
            {
                "id": "faq_003",
                "content": "Q: Do you offer customer support? A: Yes, we provide 24/7 customer support through phone, email, and live chat. Our support team is available to help with orders, technical issues, and general inquiries. Response time is typically within 2 hours.",
                "metadata": {"category": "support", "type": "service", "priority": "high"}
            },
            {
                "id": "faq_004",
                "content": "Q: What payment methods do you accept? A: We accept all major credit cards (Visa, MasterCard, American Express), PayPal, Apple Pay, Google Pay, and bank transfers. All payments are processed securely using SSL encryption.",
                "metadata": {"category": "payment", "type": "methods", "priority": "high"}
            },
            {
                "id": "faq_005",
                "content": "Q: How do I track my order? A: Once your order ships, you'll receive an email with tracking information. You can also track your order by logging into your account and viewing the order status. Tracking updates every 24 hours.",
                "metadata": {"category": "tracking", "type": "process", "priority": "medium"}
            },
            {
                "id": "faq_006",
                "content": "Q: Can I cancel my order? A: Orders can be cancelled within 1 hour of placement. After that, orders enter processing and cannot be cancelled. If you need to return an item, please refer to our return policy.",
                "metadata": {"category": "cancellation", "type": "policy", "priority": "medium"}
            },
            {
                "id": "faq_007",
                "content": "Q: Do you offer warranties on products? A: Yes, all products come with a manufacturer warranty. Electronics have a 1-year warranty, appliances have a 2-year warranty, and furniture has a 5-year warranty. Extended warranties are available for purchase.",
                "metadata": {"category": "warranty", "type": "coverage", "priority": "medium"}
            },
            {
                "id": "faq_008",
                "content": "Q: How do I create an account? A: Click 'Sign Up' on our homepage, enter your email and create a password. You'll receive a verification email. Click the link in the email to activate your account. You can then start shopping and track orders.",
                "metadata": {"category": "account", "type": "setup", "priority": "low"}
            },
            {
                "id": "faq_009",
                "content": "Q: Do you have a mobile app? A: Yes, our mobile app is available for iOS and Android devices. Download it from the App Store or Google Play. The app offers all website features plus exclusive mobile-only deals and push notifications.",
                "metadata": {"category": "mobile", "type": "app", "priority": "low"}
            },
            {
                "id": "faq_010",
                "content": "Q: What are your business hours? A: Our online store operates 24/7. Customer service is available Monday-Friday 8AM-8PM EST, weekends 10AM-6PM EST. Phone support is available during these hours, while email and chat are always available.",
                "metadata": {"category": "hours", "type": "schedule", "priority": "medium"}
            },
            {
                "id": "faq_011",
                "content": "Q: Do you offer price matching? A: Yes, we offer price matching for identical items found at authorized retailers. The item must be in stock and the price must be verifiable. Request price matching before completing your purchase.",
                "metadata": {"category": "pricing", "type": "policy", "priority": "medium"}
            },
            {
                "id": "faq_012",
                "content": "Q: How do I use a coupon code? A: Enter your coupon code at checkout in the 'Promo Code' field and click 'Apply'. The discount will be reflected in your order total. Coupon codes cannot be combined with other offers unless specified.",
                "metadata": {"category": "coupons", "type": "usage", "priority": "low"}
            },
            {
                "id": "faq_013",
                "content": "Q: What if my item arrives damaged? A: If your item arrives damaged, contact customer service within 48 hours with photos of the damage. We'll arrange for a replacement or full refund. Damaged items may need to be returned for inspection.",
                "metadata": {"category": "damage", "type": "policy", "priority": "high"}
            },
            {
                "id": "faq_014",
                "content": "Q: Do you ship internationally? A: Yes, we ship to over 50 countries worldwide. International shipping costs vary by location and weight. Customs fees and import duties are the customer's responsibility. Delivery times are 7-14 business days.",
                "metadata": {"category": "international", "type": "shipping", "priority": "medium"}
            },
            {
                "id": "faq_015",
                "content": "Q: How do I change my password? A: Log into your account, go to 'Account Settings', click 'Change Password', enter your current password and new password twice, then click 'Update'. You'll receive a confirmation email when the change is complete.",
                "metadata": {"category": "account", "type": "security", "priority": "low"}
            },
            {
                "id": "faq_016",
                "content": "Q: What is your privacy policy? A: We are committed to protecting your privacy. We only collect necessary information for order processing and account management. We never sell your personal information to third parties. View our full privacy policy on our website.",
                "metadata": {"category": "privacy", "type": "policy", "priority": "medium"}
            },
            {
                "id": "faq_017",
                "content": "Q: Do you offer bulk discounts? A: Yes, we offer bulk discounts for orders over $500. Contact our sales team for custom pricing on large orders. Business accounts receive additional discounts and priority support.",
                "metadata": {"category": "bulk", "type": "discount", "priority": "low"}
            },
            {
                "id": "faq_018",
                "content": "Q: How do I leave a product review? A: After receiving your order, you'll get an email invitation to leave a review. You can also log into your account, go to 'Order History', and click 'Write Review' next to the product. Reviews help other customers make informed decisions.",
                "metadata": {"category": "reviews", "type": "process", "priority": "low"}
            },
            {
                "id": "faq_019",
                "content": "Q: What happens if an item is out of stock? A: If an item becomes out of stock after you order, we'll notify you immediately. You can choose to wait for restock (with estimated timeline) or receive a full refund. Backorders are fulfilled in the order they were received.",
                "metadata": {"category": "stock", "type": "policy", "priority": "medium"}
            },
            {
                "id": "faq_020",
                "content": "Q: Do you offer gift cards? A: Yes, we offer digital gift cards in denominations of $25, $50, $100, and $250. Gift cards never expire and can be used for any purchase. They are delivered via email and can be printed or forwarded to recipients.",
                "metadata": {"category": "gift_cards", "type": "service", "priority": "low"}
            }
        ]

    def _create_news_dataset(self) -> List[Dict]:
        """Create news articles dataset"""
        return [
            {
                "id": "news_001",
                "content": "Tech Giant Announces Major AI Breakthrough: Researchers have developed a new neural network architecture that can process natural language 50% faster than previous models while using 30% less computational power. The breakthrough could revolutionize how AI assistants handle complex conversations.",
                "metadata": {"category": "ai", "date": "2024-01-15", "source": "TechNews Daily"}
            },
            {
                "id": "news_002",
                "content": "Quantum Computing Reaches New Milestone: Scientists successfully demonstrated quantum advantage in solving optimization problems, completing calculations in minutes that would take classical computers years. This achievement brings practical quantum computing applications closer to reality.",
                "metadata": {"category": "quantum", "date": "2024-01-20", "source": "Science Tech Report"}
            },
            {
                "id": "news_003",
                "content": "Cybersecurity Alert: Widespread Vulnerability Discovered: Security researchers uncovered a critical vulnerability affecting millions of IoT devices worldwide. The flaw could allow attackers to gain unauthorized access to smart home systems. Patches are being released urgently.",
                "metadata": {"category": "security", "date": "2024-01-25", "source": "Cyber Security Weekly"}
            },
            {
                "id": "news_004",
                "content": "Green Tech Innovation: Solar Panel Efficiency Reaches Record High: New perovskite-silicon tandem solar cells achieve 33% efficiency in laboratory tests, surpassing previous records. Mass production is expected to begin within two years, potentially reducing solar energy costs significantly.",
                "metadata": {"category": "green_tech", "date": "2024-02-01", "source": "Environmental Tech News"}
            },
            {
                "id": "news_005",
                "content": "Autonomous Vehicles Pass Major Safety Test: Self-driving cars completed 10 million test miles with zero accidents in controlled urban environments. Regulators are now considering approval for limited public road testing in select cities.",
                "metadata": {"category": "autonomous_vehicles", "date": "2024-02-05", "source": "Auto Tech Tribune"}
            },
            {
                "id": "news_006",
                "content": "Blockchain Technology Revolutionizes Supply Chain: Major retailer implements blockchain-based tracking system, providing complete transparency from manufacturer to consumer. The system reduces fraud by 90% and increases consumer confidence in product authenticity.",
                "metadata": {"category": "blockchain", "date": "2024-02-10", "source": "Supply Chain Tech"}
            },
            {
                "id": "news_007",
                "content": "5G Network Expansion Accelerates: Telecommunications companies report 5G coverage now reaches 70% of urban areas globally. The faster networks are enabling new applications in telemedicine, remote work, and augmented reality experiences.",
                "metadata": {"category": "5g", "date": "2024-02-15", "source": "Telecom Industry News"}
            },
            {
                "id": "news_008",
                "content": "Virtual Reality Healthcare Training Shows Promise: Medical students using VR simulations score 35% higher on practical exams compared to traditional training methods. Hospitals are investing heavily in VR training platforms for surgical procedures.",
                "metadata": {"category": "vr_healthcare", "date": "2024-02-20", "source": "Medical Technology Today"}
            },
            {
                "id": "news_009",
                "content": "Space Technology Milestone: Private Company Successfully Launches Reusable Rocket: The mission marks the 50th successful landing of the reusable rocket system, dramatically reducing space launch costs. The achievement paves the way for more frequent satellite deployments and space exploration missions.",
                "metadata": {"category": "space_tech", "date": "2024-02-25", "source": "Space Industry Report"}
            },
            {
                "id": "news_010",
                "content": "Edge Computing Transforms Data Processing: New edge computing infrastructure reduces data processing latency by 80% for IoT applications. This advancement enables real-time decision-making for autonomous systems and smart city applications.",
                "metadata": {"category": "edge_computing", "date": "2024-03-01", "source": "Data Center News"}
            },
            {
                "id": "news_011",
                "content": "Biotechnology Breakthrough: Gene Therapy Success Rate Improves: Clinical trials show new CRISPR-based treatments achieve 95% success rate in treating genetic disorders. The therapy has received fast-track approval for rare disease treatment.",
                "metadata": {"category": "biotech", "date": "2024-03-05", "source": "BioTech Journal"}
            },
            {
                "id": "news_012",
                "content": "Robotics in Manufacturing: Collaborative Robots Increase Productivity: Factories using collaborative robots report 40% increase in production efficiency. The robots work safely alongside human workers, handling repetitive tasks while humans focus on complex operations.",
                "metadata": {"category": "robotics", "date": "2024-03-10", "source": "Manufacturing Tech Weekly"}
            },
            {
                "id": "news_013",
                "content": "Cloud Computing Security Enhanced: Zero-Trust Architecture Adoption Surges: Enterprise adoption of zero-trust security models increases by 200% following recent cyberattacks. The approach assumes no trust by default and verifies every access request.",
                "metadata": {"category": "cloud_security", "date": "2024-03-15", "source": "Cloud Computing Today"}
            },
            {
                "id": "news_014",
                "content": "Machine Learning Democratization: No-Code AI Platform Launches: New platform allows business users to create machine learning models without programming knowledge. Early adopters report 60% reduction in AI project development time.",
                "metadata": {"category": "no_code_ai", "date": "2024-03-20", "source": "AI Business News"}
            },
            {
                "id": "news_015",
                "content": "Sustainable Computing Initiative: Data Centers Go Carbon Neutral: Major cloud providers achieve carbon neutrality through renewable energy and innovative cooling systems. The initiative reduces the tech industry's environmental footprint by 25%.",
                "metadata": {"category": "sustainable_tech", "date": "2024-03-25", "source": "Green Computing Report"}
            },
            {
                "id": "news_016",
                "content": "Augmented Reality in Education: AR Learning Apps Show Remarkable Results: Students using AR educational apps demonstrate 45% better retention rates compared to traditional textbooks. Schools are rapidly adopting AR technology for interactive learning experiences.",
                "metadata": {"category": "ar_education", "date": "2024-03-30", "source": "Education Technology News"}
            },
            {
                "id": "news_017",
                "content": "Internet Infrastructure Upgrade: New Fiber Optic Technology Increases Speed: Next-generation fiber optic cables achieve 1 terabit per second transmission speeds. The upgrade will support growing demand for high-bandwidth applications and remote work.",
                "metadata": {"category": "internet_infrastructure", "date": "2024-04-01", "source": "Network Technology Review"}
            },
            {
                "id": "news_018",
                "content": "Digital Health Revolution: Wearable Devices Predict Health Issues: Advanced wearables can now predict potential health problems 72 hours before symptoms appear. The technology uses AI to analyze biometric patterns and alert users and healthcare providers.",
                "metadata": {"category": "digital_health", "date": "2024-04-05", "source": "Health Tech Innovation"}
            },
            {
                "id": "news_019",
                "content": "Cryptocurrency Market Evolution: Central Bank Digital Currencies Gain Momentum: Multiple countries announce plans for central bank digital currencies (CBDCs) as digital payment adoption accelerates. Pilot programs show promising results for financial inclusion.",
                "metadata": {"category": "cryptocurrency", "date": "2024-04-10", "source": "Financial Technology Times"}
            },
            {
                "id": "news_020",
                "content": "Smart City Technology: AI-Powered Traffic Management Reduces Congestion: Cities implementing AI traffic management systems report 30% reduction in traffic congestion. The technology optimizes traffic light timing and route suggestions in real-time.",
                "metadata": {"category": "smart_cities", "date": "2024-04-15", "source": "Urban Technology Report"}
            }
        ]

    def _populate_collection(self, collection_name: str, documents: List[Dict]):
        """Populate ChromaDB collection with documents"""
        try:
            # Try to delete existing collection and create fresh one
            try:
                self.client.delete_collection(collection_name)
                print(f"Deleted existing collection: {collection_name}")
            except:
                print(
                    f"Collection {collection_name} doesn't exist, creating new one")

            # Create fresh collection
            collection = self.client.create_collection(collection_name)

            # Prepare data for ChromaDB
            ids = []
            texts = []
            metadatas = []
            embeddings = []

            print(
                f"Processing {len(documents)} documents for {collection_name}...")

            for doc in documents:
                # Get embedding for the document content
                embedding = self._get_embedding(doc['content'])
                if embedding:
                    ids.append(doc['id'])
                    texts.append(doc['content'])
                    metadatas.append(doc['metadata'])
                    embeddings.append(embedding)
                    print(f"Processed {doc['id']}")
                else:
                    print(f"Failed to get embedding for {doc['id']}")

            # Add to collection
            if ids:
                collection.add(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
                print(
                    f"Successfully added {len(ids)} documents to {collection_name}")
            else:
                print(f"No documents were added to {collection_name}")

        except Exception as e:
            print(f"Error populating collection {collection_name}: {e}")

    def setup_all_datasets(self):
        """Setup all datasets in ChromaDB"""
        print("Setting up RAG Playground datasets...")

        # Create datasets
        tech_docs = self._create_tech_docs_dataset()
        faq_data = self._create_faq_dataset()
        news_articles = self._create_news_dataset()

        # Populate collections
        self._populate_collection("tech_docs", tech_docs)
        self._populate_collection("faq_data", faq_data)
        self._populate_collection("news_articles", news_articles)

        print("Dataset setup complete!")

        # Print summary
        print("\n=== Dataset Summary ===")
        for collection_name in ["tech_docs", "faq_data", "news_articles"]:
            try:
                collection = self.client.get_collection(collection_name)
                count = collection.count()
                print(f"{collection_name}: {count} documents")
            except:
                print(f"{collection_name}: Collection not found")


if __name__ == "__main__":
    processor = DataPrep()
    processor.setup_all_datasets()
