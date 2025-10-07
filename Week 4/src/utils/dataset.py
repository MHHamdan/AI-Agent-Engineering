"""
Dataset Management Module

Manages evaluation datasets for the RAG system, including test questions and reference answers.
"""

from typing import List, Dict, Any
from langsmith import Client
from src.config import Config
import logging

logger = logging.getLogger(__name__)


# Evaluation examples with reference answers
EVALUATION_EXAMPLES = [
    {
        "inputs": {"question": "What are the prohibited AI practices under the EU AI Act?"},
        "outputs": {
            "expected_answer": "The EU AI Act prohibits AI practices that pose unacceptable risks, including: (1) AI systems that deploy subliminal techniques to materially distort behavior causing harm, (2) AI systems exploiting vulnerabilities of specific groups causing harm, (3) biometric categorization systems using sensitive characteristics, (4) social scoring systems by public authorities, (5) AI systems assessing risk of committing criminal offenses based solely on profiling, (6) creating or expanding facial recognition databases through untargeted scraping, (7) emotion recognition in workplace and educational institutions (with limited exceptions), (8) real-time remote biometric identification in publicly accessible spaces for law enforcement (with limited exceptions)."
        },
        "metadata": {"category": "prohibited_practices"}
    },
    {
        "inputs": {"question": "What is a high-risk AI system according to the EU AI Act?"},
        "outputs": {
            "expected_answer": "A high-risk AI system is one that falls into specific categories listed in Annex III of the EU AI Act or is used as a safety component of products covered by Union harmonization legislation. High-risk AI systems include those used in: biometric identification, critical infrastructure management, education and vocational training, employment and worker management, access to essential services, law enforcement, migration and border control management, and administration of justice. These systems pose significant risks to health, safety, or fundamental rights."
        },
        "metadata": {"category": "definitions"}
    },
    {
        "inputs": {"question": "What are the requirements for providers of high-risk AI systems?"},
        "outputs": {
            "expected_answer": "Providers of high-risk AI systems must: (1) establish and maintain a risk management system, (2) ensure appropriate data governance and quality, (3) prepare technical documentation, (4) implement automatic logging capabilities, (5) provide clear and adequate information to users, (6) design systems for human oversight, (7) ensure appropriate levels of accuracy, robustness, and cybersecurity, (8) establish a quality management system, (9) conduct conformity assessments, (10) register the system in the EU database, (11) take corrective actions when needed, and (12) cooperate with authorities during investigations."
        },
        "metadata": {"category": "compliance"}
    },
    {
        "inputs": {"question": "What is the conformity assessment procedure for high-risk AI systems?"},
        "outputs": {
            "expected_answer": "The conformity assessment for high-risk AI systems involves either: (1) Internal control procedure - where the provider verifies compliance based on technical documentation and quality management system, or (2) Assessment by a notified body - for certain systems listed in Annex III. The procedure includes checking compliance with requirements in Chapter 2, preparing technical documentation, implementing a quality management system, and maintaining records. After successful assessment, the provider affixes the CE marking and draws up an EU declaration of conformity."
        },
        "metadata": {"category": "procedures"}
    },
    {
        "inputs": {"question": "What are the transparency requirements for AI systems?"},
        "outputs": {
            "expected_answer": "The EU AI Act establishes transparency obligations including: (1) AI systems intended to interact with people must be designed to inform users they are interacting with AI (unless obvious from context), (2) emotion recognition and biometric categorization systems must inform users when they are being used, (3) AI-generated content (deep fakes) must be disclosed and marked as artificially generated or manipulated, (4) users of AI systems that generate or manipulate text, audio, or video content must disclose that the content is AI-generated, and (5) providers must ensure outputs are marked in a machine-readable format when technically feasible."
        },
        "metadata": {"category": "transparency"}
    },
    {
        "inputs": {"question": "What are the obligations of deployers of high-risk AI systems?"},
        "outputs": {
            "expected_answer": "Deployers of high-risk AI systems must: (1) use the system according to instructions of use, (2) ensure human oversight, (3) monitor the system's operation and inform the provider or distributor of incidents and malfunctions, (4) keep logs automatically generated by the system for at least 6 months (or longer as specified), (5) conduct a data protection impact assessment when required by GDPR, (6) ensure input data is relevant and representative, (7) cooperate with authorities, and (8) for certain systems like those used in employment or law enforcement, inform affected persons about the use of the AI system."
        },
        "metadata": {"category": "compliance"}
    }
]


class DatasetManager:
    """
    Manages evaluation datasets in LangSmith.

    This class handles:
    - Creating datasets in LangSmith
    - Adding examples to datasets
    - Managing dataset versions
    - Retrieving dataset information
    """

    def __init__(self, dataset_name: str = Config.DATASET_NAME):
        """
        Initialize the dataset manager.

        Args:
            dataset_name: Name of the dataset in LangSmith
        """
        self.dataset_name = dataset_name
        self.client = Client()

        logger.info(f"DatasetManager initialized for dataset: {dataset_name}")

    def create_dataset(
        self,
        examples: List[Dict[str, Any]] = None,
        description: str = None
    ) -> Any:
        """
        Creates or updates a dataset in LangSmith.

        Args:
            examples: List of evaluation examples (uses default if None)
            description: Description of the dataset

        Returns:
            Dataset object from LangSmith
        """
        if examples is None:
            examples = EVALUATION_EXAMPLES

        if description is None:
            description = "EU AI Act RAG evaluation dataset with compliance questions and reference answers"

        logger.info(f"Creating dataset: {self.dataset_name} with {len(examples)} examples")

        try:
            # Try to create new dataset
            dataset = self.client.create_dataset(
                dataset_name=self.dataset_name,
                description=description
            )

            logger.info(f"✓ Created new dataset with ID: {dataset.id}")

        except Exception as e:
            if "already exists" in str(e):
                # Use existing dataset
                dataset = self.client.read_dataset(dataset_name=self.dataset_name)
                logger.info(f"✓ Using existing dataset with ID: {dataset.id}")
            else:
                logger.error(f"Error creating dataset: {e}")
                raise

        # Add examples to dataset
        try:
            self.client.create_examples(
                dataset_id=dataset.id,
                examples=examples
            )
            logger.info(f"✓ Added {len(examples)} examples to dataset")

        except Exception as e:
            logger.warning(f"Some examples may already exist: {e}")

        return dataset

    def get_dataset(self) -> Any:
        """
        Retrieves the dataset from LangSmith.

        Returns:
            Dataset object

        Raises:
            ValueError: If dataset doesn't exist
        """
        try:
            dataset = self.client.read_dataset(dataset_name=self.dataset_name)
            logger.info(f"Retrieved dataset: {dataset.id}")
            return dataset

        except Exception as e:
            logger.error(f"Dataset not found: {e}")
            raise ValueError(f"Dataset '{self.dataset_name}' not found. Create it first.")

    def get_examples(self) -> List[Any]:
        """
        Get all examples from the dataset.

        Returns:
            List of example objects
        """
        dataset = self.get_dataset()
        examples = list(self.client.list_examples(dataset_id=dataset.id))
        logger.info(f"Retrieved {len(examples)} examples from dataset")
        return examples

    def get_dataset_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the dataset.

        Returns:
            Dictionary with dataset statistics
        """
        try:
            dataset = self.get_dataset()
            examples = self.get_examples()

            # Count categories
            categories = {}
            for example in examples:
                category = example.metadata.get("category", "unknown") if hasattr(example, "metadata") else "unknown"
                categories[category] = categories.get(category, 0) + 1

            return {
                "dataset_name": self.dataset_name,
                "dataset_id": str(dataset.id),
                "total_examples": len(examples),
                "categories": categories
            }

        except Exception as e:
            logger.error(f"Error getting dataset stats: {e}")
            return {"error": str(e)}


def setup_evaluation_dataset() -> str:
    """
    Convenience function to set up the evaluation dataset.

    Returns:
        Dataset name
    """
    manager = DatasetManager()
    manager.create_dataset()
    return manager.dataset_name
