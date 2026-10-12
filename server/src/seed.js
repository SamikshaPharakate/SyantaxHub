require('dotenv').config({ path: __dirname + '/../.env' });
const mongoose = require('mongoose');
const User = require('./models/User');
const Snippet = require('./models/Snippet');
const Analysis = require('./models/Analysis');
const aiMicroservice = require('./services/aiMicroservice');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/syntaxhub';

const seedDatabase = async () => {
  try {
    console.log(`[Seed] Connecting to MongoDB at ${MONGO_URI}...`);
    await mongoose.connect(MONGO_URI);
    console.log('[Seed] Database connected successfully.');

    // 1. Create or ensure Demo User
    const demoEmail = 'demo@syntaxhub.dev';
    let user = await User.findOne({ email: demoEmail });
    if (!user) {
      user = await User.create({
        name: 'Jordan Davis (Demo)',
        email: demoEmail,
        password: 'syntaxhub-demo-password-2026',
        role: 'user',
      });
      console.log(`[Seed] Created Demo User: ${user.email}`);
    } else {
      console.log(`[Seed] Demo User already exists: ${user.email}`);
    }

    // 2. Clear & Seed Snippets
    await Snippet.deleteMany({});
    console.log('[Seed] Cleared existing code snippets.');

    const initialSnippets = [
      {
        title: 'React 19 Async Action Transition Pattern',
        language: 'javascript',
        code: `import { useTransition } from "react";\n\nexport function UpdateName() {\n  const [isPending, startTransition] = useTransition();\n  \n  const handleSubmit = (formData) => {\n    startTransition(async () => {\n      const error = await updateNameAction(formData.get("name"));\n      if (error) {\n        console.error(error);\n      }\n    });\n  };\n}`,
        description: 'Modern React 19 async transition pattern replacing legacy state locks and custom loading flags.',
        tags: ['react19', 'async', 'transitions', 'hooks'],
        user: user._id,
        isPublic: true,
      },
      {
        title: 'Java 21 Virtual Threads Executing Concurrent Tasks',
        language: 'java',
        code: `import java.util.concurrent.Executors;\n\npublic class VirtualThreadDemo {\n    public static void main(String[] args) {\n        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {\n            for (int i = 0; i < 1000; i++) {\n                final int taskId = i;\n                executor.submit(() -> {\n                    System.out.println("Processing task " + taskId + " on " + Thread.currentThread());\n                    return taskId;\n                });\n            }\n        }\n    }\n}`,
        description: 'Java 21 Project Loom virtual threads for ultra lightweight concurrency.',
        tags: ['java21', 'virtual-threads', 'loom', 'concurrency'],
        user: user._id,
        isPublic: true,
      },
      {
        title: 'Python 3.13 Generic Type Annotation Syntax',
        language: 'python',
        code: `def get_first_element[T](items: list[T]) -> T:\n    """PEP 695 type parameter syntax introduced in Python 3.12+ / 3.13."""\n    if not items:\n        raise ValueError("List is empty")\n    return items[0]`,
        description: 'Clean inline type parameter syntax replacing old TypeVar boilerplates.',
        tags: ['python313', 'typing', 'pep695', 'generics'],
        user: user._id,
        isPublic: true,
      },
      {
        title: 'JavaScript Object.groupBy Standard API',
        language: 'javascript',
        code: `const inventory = [\n  { name: "apples", category: "fruit", quantity: 5 },\n  { name: "bananas", category: "fruit", quantity: 0 },\n  { name: "carrots", category: "vegetable", quantity: 10 }\n];\n\nconst result = Object.groupBy(inventory, ({ category }) => category);`,
        description: 'Native ES2024 Object.groupBy method replacing manual array reduce grouping.',
        tags: ['es2024', 'javascript', 'array', 'grouping'],
        user: user._id,
        isPublic: true,
      },
    ];

    const createdSnippets = await Snippet.insertMany(initialSnippets);
    console.log(`[Seed] Seeded ${createdSnippets.length} initial snippets into MongoDB.`);

    // 3. Clear & Seed Saved Analyses
    await Analysis.deleteMany({});
    console.log('[Seed] Cleared existing analyses.');

    const initialAnalyses = [
      {
        title: 'React 19 async patterns audit',
        technology: 'React',
        language: 'javascript',
        version: '19',
        code: `useEffect(() => {\n  fetchUser(userId).then(result => setUser(result))\n}, [userId])`,
        result: {
          summary: 'Detected client-side waterfall data fetching pattern.',
          recommendation: 'Use React 19 Server Components or use() Hook with Suspense boundaries.',
        },
        status: 'outdated',
        isSaved: true,
        user: user._id,
      },
      {
        title: 'Java 21 Loom concurrency review',
        technology: 'Java',
        language: 'java',
        version: '21',
        code: `var executor = Executors.newFixedThreadPool(100);`,
        result: {
          summary: 'Legacy OS fixed thread pool detected.',
          recommendation: 'Replace with Executors.newVirtualThreadPerTaskExecutor() in Java 21.',
        },
        status: 'outdated',
        isSaved: true,
        user: user._id,
      },
    ];

    const createdAnalyses = await Analysis.insertMany(initialAnalyses);
    console.log(`[Seed] Seeded ${createdAnalyses.length} analyses into MongoDB.`);

    // 4. Try auto-indexing snippets into Python Vector Service if running
    console.log('[Seed] Attempting vector DB auto-indexing via AI Microservice...');
    let indexedCount = 0;
    for (const snip of createdSnippets) {
      try {
        await aiMicroservice.indexSnippet({
          id: snip._id.toString(),
          title: snip.title,
          language: snip.language,
          code: snip.code,
          description: snip.description,
        });
        await Snippet.findByIdAndUpdate(snip._id, { vectorIndexed: true });
        indexedCount++;
      } catch (err) {
        console.warn(`[Seed Note] AI Microservice index skipped for '${snip.title}': ${err.message}`);
      }
    }

    if (indexedCount > 0) {
      console.log(`[Seed] Successfully indexed ${indexedCount} snippets into Python ChromaDB.`);
    } else {
      console.log('[Seed] AI Microservice was offline during seeding. Snippets will auto-index when requested.');
    }

    console.log('[Seed] Database seeding completed successfully! ✅');
    process.exit(0);
  } catch (err) {
    console.error('[Seed Error] Failed to seed database:', err);
    process.exit(1);
  }
};

seedDatabase();
